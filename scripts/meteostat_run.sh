start=`date +%s`
pip install -r requirements.txt

python setup.py develop

pip install -r requirements.txt --upgrade

file="Meteostat_searchable_province.txt"

# Check if the file exists
if [ -r "$file" ]; then
    # Read each line from the file and pass it to the Python script
   content=$(<"$file")
    
    # Loop through each line and process it
   while IFS= read -r line; do
      # Process each line individually (for example, print it)
   province=$(echo "$line" | sed -e 's/[^[:print:]]//g') #Remember to remove all hidden part of the line
   python src/Meteostat_crawler.py --province_name=$province --days=1  
   done <<< "$content"
else
   echo "Error: Unable to read file $file"
fi

end=`date +%s`
echo Execution time was `expr $end - $start` seconds.