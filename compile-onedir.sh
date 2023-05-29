pyinstaller --noconfirm --distpath "../Blood Emporium Output" "onedir.spec"
mkdir "../Blood Emporium Output/Blood Emporium/logs"
mkdir "../Blood Emporium Output/Blood Emporium/exports"

if [ "$2" == "dev" ]; then
    mkdir "../Blood Emporium Output/Blood Emporium/output"
fi

rm -r build
mv "../Blood Emporium Output/Blood Emporium" "../Blood Emporium Output/Blood Emporium ${1}"

echo "Press any button to continue..."
read -n1