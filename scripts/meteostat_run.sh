start=`date +%s`
pip install -r requirements.txt

python setup.py develop

pip install -r requirements.txt --upgrade

declare -a vietnamese_locations=('AnGiang' 'BacLieu' 'BacGiang' 'BacNinh' 'VungTau' 'BenTre' 'BinhDinh' 'BinhDuong' 'BinhPhuoc' 'BinhThuan' 'CaMau' 'CaoBang' 'DakLak' 'DakNong' 'DienBien' 'DongNai' 'DongThap' 'GiaLai' 'HaGiang' 'HaNam' 'HaTinh' 'HaiDuong' 'HauGiang' 'HoaBinh' 'HungYen' 'KhanhHoa' 'KienGiang' 'KonTum' 'LaiChau' 'LamDong' 'LangSon' 'LaoCai' 'LongAn' 'NamDinh' 'NgheAn' 'NinhBinh' 'NinhThuan' 'PhuTho' 'PhuYen' 'QuangBinh' 'QuangNam' 'QuangNgai' 'QuangNinh' 'QuangTri' 'SocTrang' 'SonLa' 'TayNinh' 'ThaiBinh' 'ThaiNguyen' 'ThanhHoa' 'Hue' 'TienGiang' 'TraVinh' 'TuyenQuang' 'VinhLong' 'VinhPhuc' 'YenBai' 'CanTho' 'DaNang' 'HaNoi' 'HaiPhong' 'HoChiMinh')
for i in "${vietnamese_locations[@]}"
do
   python src/Meteostat_crawler.py --province_name=$i --days=1  
done
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.