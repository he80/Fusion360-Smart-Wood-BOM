import adsk.core, adsk.fusion, traceback
import os
import csv
import math
import re

# --- USER SETTINGS ---
PRICE_PER_M3_NIS = 1800.0   
SAW_KERF = 4  
STOCK_MARKET_SIZES = [2400, 2700, 3000, 3300, 3600, 3900, 4200, 4500, 4800, 5100, 5400, 5700, 6000]
USE_SNAPPING = True
SNAP_INTERVAL = 5 
# ---------------------

# Global Variables for UI
app = None
ui = None
handlers = []
CMD_ID = 'SmartWoodBOM_Btn'
CMD_NAME = 'Export Wood BOM'
CMD_TOOLTIP = 'Generate Cut List & Cost Report'

# --- HELPER FUNCTIONS (Your Logic) ---
def clean_part_name(name):
    name = name.split(':')[0]
    name = re.sub(r'\s*v\d+$', '', name)
    name = re.sub(r'\s*\(\d+\)$', '', name)
    return name.strip()

def smart_round(value):
    if USE_SNAPPING:
        return int(round(value / SNAP_INTERVAL) * SNAP_INTERVAL)
    return int(round(value))

def get_best_orientation(body):
    longest_edge = None
    max_len = 0
    for edge in body.edges:
        if edge.geometry.curveType != adsk.core.Curve3DTypes.Line3DCurveType: continue
        l = edge.length
        if l > max_len:
            max_len = l
            longest_edge = edge
            
    if longest_edge:
        start = longest_edge.startVertex.geometry
        end = longest_edge.endVertex.geometry
        length_vector = start.vectorTo(end)
        length_vector.normalize()
        best_face_normal = None
        for face in body.faces:
            if face.geometry.objectType != adsk.core.Plane.classType(): continue
            normal = face.geometry.normal
            normal.normalize()
            if abs(normal.dotProduct(length_vector)) < 0.1:
                best_face_normal = normal
                break
        if best_face_normal:
            y_axis = best_face_normal
            x_axis = length_vector.crossProduct(y_axis)
            return (length_vector, x_axis, y_axis)

    physProps = body.getPhysicalProperties(adsk.fusion.CalculationAccuracy.HighCalculationAccuracy)
    (_, xAxis, yAxis, zAxis) = physProps.getPrincipalAxes()
    moments = [physProps.getPrincipalMomentsOfInertia()[1], physProps.getPrincipalMomentsOfInertia()[2], physProps.getPrincipalMomentsOfInertia()[3]]
    axes = [xAxis, yAxis, zAxis]
    min_idx = moments.index(min(moments))
    length_vec = axes[min_idx]
    other_axes = [a for i, a in enumerate(axes) if i != min_idx]
    return (length_vec, other_axes[0], other_axes[1])

def get_optimized_shopping_list(parts_lengths):
    parts_lengths.sort(reverse=True)
    boards = []
    max_len = 6000
    
    for part in parts_lengths:
        part_needed = part + SAW_KERF
        placed = False
        for board in boards:
            if (board['capacity'] - board['used']) >= part_needed:
                board['used'] += part_needed
                board['cuts'].append(part)
                placed = True
                break
        if not placed:
            boards.append({'capacity': max_len, 'used': part_needed, 'cuts': [part]})

    final_shopping_list = []
    for board in boards:
        used_len = board['used']
        best_fit = 6000 
        for size in STOCK_MARKET_SIZES:
            if size >= used_len:
                best_fit = size
                break
        final_shopping_list.append(best_fit)
    return final_shopping_list

# --- MAIN LOGIC (Runs when button is clicked) ---
def main_export_logic():
    design = app.activeProduct
    root = design.rootComponent
    
    bom_data = {}
    stock_data = {}

    def process_body(body, raw_name):
        if not body.isSolid: return
        try:
            (length_vector, axis2, axis3) = get_best_orientation(body)
            length_vector.normalize()
            axis2.normalize()

            measureMgr = app.measureManager
            obb = measureMgr.getOrientedBoundingBox(body, length_vector, axis2)
            
            raw_dims = [obb.length, obb.width, obb.height]
            raw_dims.sort(reverse=True)
            
            l = int(round(raw_dims[0] * 10)) 
            h = smart_round(raw_dims[1] * 10) 
            w = smart_round(raw_dims[2] * 10) 
            mat = body.material.name
            
            found_angles = []
            for face in body.faces:
                geom = face.geometry
                if geom.objectType != adsk.core.Plane.classType(): continue
                normal = geom.normal
                normal.normalize()
                dot = abs(normal.dotProduct(length_vector))
                if dot < 0.1: continue 
                angle_deg = math.degrees(math.acos(dot))
                found_angles.append(round(angle_deg * 2) / 2)

            unique_angles = sorted(list(set(found_angles)))
            a1 = f"{unique_angles[0]}°" if len(unique_angles) > 0 else "90.0°"
            a2 = f"{unique_angles[1]}°" if len(unique_angles) > 1 else a1

            final_name = clean_part_name(raw_name)
            bom_key = (final_name, mat, l, h, w, a1, a2)
            
            if bom_key in bom_data: bom_data[bom_key] += 1
            else: bom_data[bom_key] = 1
                
            stock_key = (mat, h, w)
            if stock_key in stock_data: stock_data[stock_key].append(l)
            else: stock_data[stock_key] = [l]
        except:
            return 

    # Scan
    for body in root.bRepBodies:
        if body.isLightBulbOn: process_body(body, "RootBody")
    for occ in root.allOccurrences:
        if not occ.isVisible: continue
        comp = occ.component
        for body in comp.bRepBodies:
            if body.isLightBulbOn: process_body(body, occ.name)

    if not bom_data:
        ui.messageBox("No parts found.")
        return

    file_path = os.path.join(os.path.expanduser("~"), "Desktop", "Fusion_Cost_Report.csv")
    
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        writer.writerow(['Project Cost Report', '', '', '', '', '', '', '', '', ''])
        writer.writerow(['Unit Price Used (NIS/m3):', PRICE_PER_M3_NIS, '', '', '', '', '', '', '', ''])
        writer.writerow([]) 

        # Table 1
        writer.writerow(['--- 1. NET PARTS LIST ---'])
        writer.writerow(['Part Name', 'Material', 'Qty', 'Gross Length (mm)', 'Height', 'Width', 'Ang 1', 'Ang 2', 'Net Vol (m3)', 'Net Cost'])
        
        total_net_cost = 0
        sorted_bom = sorted(bom_data.items(), key=lambda x: x[0][0]) 
        
        for key, qty in sorted_bom:
            (name, mat, l, h, w, a1, a2) = key
            vol = (l * h * w * qty) / 1e9
            cost = vol * PRICE_PER_M3_NIS
            total_net_cost += cost
            writer.writerow([name, mat, qty, l, h, w, a1, a2, round(vol, 4), round(cost, 2)])
            
        writer.writerow(['', '', '', '', '', '', '', '', 'NET TOTAL:', round(total_net_cost, 2)])
        writer.writerow([])
        writer.writerow([])
        
        # Table 2
        writer.writerow(['--- 2. SHOPPING LIST ---'])
        writer.writerow(['Qty', 'Stock Length to Buy (mm)', 'Material', 'Height', 'Width', 'Board Vol (m3)', 'Board Cost'])
        
        grand_total_purchase_price = 0
        
        for stock_key, lengths_needed in stock_data.items():
            (mat, h, w) = stock_key
            optimized_boards = get_optimized_shopping_list(lengths_needed)
            
            board_counts = {}
            for board_len in optimized_boards:
                if board_len in board_counts: board_counts[board_len] += 1
                else: board_counts[board_len] = 1
            
            for b_len, b_qty in board_counts.items():
                board_vol = (b_len * h * w * b_qty) / 1e9
                board_cost = board_vol * PRICE_PER_M3_NIS
                grand_total_purchase_price += board_cost
                writer.writerow([b_qty, b_len, mat, h, w, round(board_vol, 4), round(board_cost, 2)])

        writer.writerow([])
        writer.writerow(['', '', '', '', '', '', 'TOTAL PURCHASE PRICE:', round(grand_total_purchase_price, 2)])

    ui.messageBox(f'Report Saved to Desktop!\nTotal Purchase: {round(grand_total_purchase_price, 2)} NIS')

# --- BUTTON EVENT HANDLER ---
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            main_export_logic()
        except:
            if ui: ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = args.command
            onExecute = CommandExecuteHandler()
            cmd.execute.add(onExecute)
            handlers.append(onExecute) # Keep handler alive
        except:
            if ui: ui.messageBox('Panel Create Failed:\n{}'.format(traceback.format_exc()))

# --- RUN / STOP (ADD-IN LIFECYCLE) ---
def run(context):
    global app, ui
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # 1. Create the Button Definition
        cmdDef = ui.commandDefinitions.itemById(CMD_ID)
        if not cmdDef:
            cmdDef = ui.commandDefinitions.addButtonDefinition(CMD_ID, CMD_NAME, CMD_TOOLTIP, '')
        
        # 2. Connect the Button to Code
        onCommandCreated = CommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        handlers.append(onCommandCreated)
        
        # 3. Add Button to "Utilities" -> "ADD-INS" Panel
        targetPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        if targetPanel:
            targetPanel.controls.addCommand(cmdDef)
            
    except:
        if ui: ui.messageBox('Failed to start:\n{}'.format(traceback.format_exc()))

def stop(context):
    try:
        # CLEANUP: Remove the button when Add-In stops
        targetPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        btn = targetPanel.controls.itemById(CMD_ID)
        if btn: btn.deleteMe()
        
        cmdDef = ui.commandDefinitions.itemById(CMD_ID)
        if cmdDef: cmdDef.deleteMe()
            
    except:
        if ui: ui.messageBox('Failed to stop:\n{}'.format(traceback.format_exc()))