pyinstaller --noconfirm --onedir --windowed --name "Blood Emporium ${1}" --icon "references/inspo1.ico" --add-data "assets;assets/" --paths "backend" --distpath "../Blood Emporium Output" "main.py"
mkdir "../Blood Emporium Output/Blood Emporium ${1}/logs"

if [ "$2" == "dev" ]; then
    mkdir "../Blood Emporium Output/Blood Emporium ${1}/output"
fi

rm -r build

echo "Press any button to continue..."
read -n1