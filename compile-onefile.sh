mkdir "../Blood Emporium Output/Blood Emporium ${1}"
pyinstaller --noconfirm --onefile --windowed --name "Blood Emporium" --icon "references/inspo1.ico" --paths "backend" --distpath "../Blood Emporium Output/Blood Emporium ${1}" "main.py"
cp -r "assets" "../Blood Emporium Output/Blood Emporium ${1}/assets"
mkdir "../Blood Emporium Output/Blood Emporium ${1}/logs"

if [ "$2" == "dev" ]; then
    mkdir "../Blood Emporium Output/Blood Emporium ${1}/output"
fi

rm -r build

echo "Press any button to continue..."
read -n1