# Python 自製自動連點器

## 開發動機

最初使用朋友推薦的連點器時，我發現軟體介面以英文呈現，部分功能與設定選項不容易理解，操作上也不太順手。

因此，我決定使用 Python 的 PyQt6 套件，從頭開始開發一套符合自身需求的自動連點工具。

開發過程中，我不只著重於自動點擊功能，也考慮到操作介面的易用性，提供繁體中文與英文雙語切換介面，並設計可調整的點擊設定，讓使用者能更直覺地操作軟體。

透過這個專案，我希望將 Python 程式設計、GUI 開發與實際問題解決結合，打造一套兼具實用性與易用性的桌面應用程式。

---

## 使用套件

本專案使用以下 Python 套件：

- **PyAutoGUI**：執行滑鼠自動點擊等操作。
- **pynput**：控制滑鼠輸入。
- **PyQt6**：建立桌面圖形使用者介面。

### 執行程式

在專案目錄中執行：

```bash
python mouse_auto_clicker.py
```

### 安裝方式

請在終端機或命令提示字元執行：

```bash
python -m pip install pyautogui pynput PyQt6
```

---

## 程式打包方式

使用 PyInstaller 將 Python 程式打包成 Windows 可執行檔。

### 1. 安裝 PyInstaller

```bash
python -m pip install pyinstaller
```

### 2. 執行打包

```bash
python -m PyInstaller --onefile --windowed mouse_auto_clicker.py
```

### 3. 取得執行檔

打包完成後，可在 `dist` 資料夾中找到：

```text
dist/
└── mouse_auto_clicker.exe
```


---

## 授權條款

本專案由作者自行撰寫的程式碼及相關文件，採用 **GNU General Public License v3.0 only（GPL-3.0-only）** 授權。完整授權條款請參閱專案根目錄中的 [LICENSE](LICENSE)。

簡單來說，任何人都可以使用、研究、修改及散布本專案；但若散布本專案或其衍生作品，必須遵守 GPL-3.0-only 的條款，包括提供相應原始碼，並以相同授權條款散布受 GPL 規範的衍生作品。

### 第三方套件

本專案使用的第三方套件並非由本專案重新授權，仍各自適用其原作者或維護者提供的授權條款：

- **PyAutoGUI**：BSD License
- **pynput**：GNU Lesser General Public License v3.0（LGPL-3.0）
- **PyQt6**：GNU General Public License v3.0 或 Riverbank 商業授權

散布打包後的可執行檔時，請一併確認所有實際包含的第三方元件及其相依套件之授權與散布要求，並提供 GPL 所要求的相應原始碼及授權聲明。
