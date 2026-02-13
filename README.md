![GitHub all releases](https://img.shields.io/github/downloads/he80/Fusion360-Smart-Wood-BOM/total?style=for-the-badge&label=Downloads&color=success)

![GitHub repo size](https://img.shields.io/github/repo-size/he80/Fusion360-Smart-Wood-BOM?style=for-the-badge&color=blue)

![GitHub views](https://komarev.com/ghpvc/?username=he80-Fusion360-Smart-Wood-BOM&label=Views&color=orange&style=for-the-badge)

\# Fusion 360 Smart Wood BOM \& Cost Estimator



A powerful Add-in for Autodesk Fusion 360 that generates intelligent Cut Lists, Bill of Materials (BOM), and optimized Shopping Lists for woodworking and metalworking projects.




<img width="1068" height="501" alt="bom" src="https://github.com/user-attachments/assets/4adb741e-176f-4081-8877-12b9177a74c4" />


\## 🚀 Features



\* \*\*Smart Grouping:\*\* Automatically groups identical parts even if Fusion names them `Leg (1)`, `Leg (2)`, etc.

\* \*\*Geometry Intelligence:\*\* Uses "Longest Edge" detection to find the true dimensions of a part, even if it has notches, dados, or 45-degree miter cuts.

\* \*\*Angle Detection:\*\* Automatically detects cut angles (e.g., 45°, 30°) and adds them to the report.

\* \*\*Stock Optimization:\*\*

&nbsp;   \* Calculates exactly how many raw boards you need to buy.

&nbsp;   \* Optimizes for 6.0m stock but automatically "downsizes" to smaller standard lengths (3.0m, 2.4m, etc.) if a full board isn't needed.

\* \*\*Cost Estimation:\*\*

&nbsp;   \* \*\*Net Cost:\*\* Value of the wood inside the finished project.

&nbsp;   \* \*\*Gross Cost:\*\* Total purchase price at the lumber yard (including waste).

&nbsp;   \* Includes an editable "Unit Price" field in the CSV for quick recalculations.



\## 📦 Installation



1\.  Download this repository as a ZIP file.

2\.  Unzip the folder and rename it to `SmartWoodBOM`.

3\.  Move the folder to your Fusion 360 Add-ins directory:

&nbsp;   \* \*\*Windows:\*\* `%appdata%\\Autodesk\\Autodesk Fusion 360\\API\\AddIns\\`

&nbsp;   \* \*\*Mac:\*\* `~/Library/Application Support/Autodesk/Autodesk Fusion 360/API/AddIns/`

4\.  Open Fusion 360.

5\.  Go to \*\*Utilities > Scripts and Add-Ins\*\*.

6\.  Select \*\*SmartWoodBOM\*\* in the "Add-Ins" tab and click \*\*Run\*\*.

7\.  Check "Run on Startup" to keep the button available.



\## 🛠 Usage



1\.  Open your woodworking/metal design in Fusion 360.

2\.  Go to the \*\*Utilities\*\* tab.

3\.  Click the new \*\*"Export Wood BOM"\*\* button.

<img width="651" height="221" alt="1" src="https://github.com/user-attachments/assets/baeaab7e-5923-4209-8de1-841622eb5262" />

4\.  A CSV file (Excel) will be saved to your Desktop containing:

&nbsp;   \* \*\*Cut List:\*\* Exact dimensions for the saw.

&nbsp;   \* \*\*Shopping List:\*\* What to buy from the store.



\## ⚙️ Customization



You can edit the top of the `SmartWoodBOM.py` file to change:

\* `PRICE\_PER\_M3\_NIS`: Your local wood price.

\* `SAW\_KERF`: The thickness of your saw blade (default 4mm).

\* `STOCK\_MARKET\_SIZES`: The standard board lengths available in your country.



\## 📄 License



This project is licensed under the MIT License - free to use and modify!







