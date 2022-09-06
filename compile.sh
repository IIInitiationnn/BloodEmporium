pyinstaller --noconfirm --onedir --windowed --name "Blood Emporium" --icon "E:/Coding Projects/Blood Emporium/references/inspo1.ico" --add-data "E:/Coding Projects/Blood Emporium/assets;assets/" --paths "E:/Coding Projects/Blood Emporium/backend" --distpath "E:\Coding Projects\Blood Emporium Output" "E:/Coding Projects/Blood Emporium/main.py"
mkdir "..\Blood Emporium Output\Blood Emporium\logs"

if [ "$2" == "dev" ]; then
    mkdir "..\Blood Emporium Output\Blood Emporium\output"
fi

rm -r build
mv "E:\Coding Projects\Blood Emporium Output\Blood Emporium" "E:\Coding Projects\Blood Emporium Output\Blood Emporium ${1}"

read -n1