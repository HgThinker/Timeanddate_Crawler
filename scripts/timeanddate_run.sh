start=`date +%s`

file="Timeanddate_searchable_province.txt"

# Check if the file exists
if [ -r "$file" ]; then
    # Read each line from the file and pass it to the Python script
   content=$(<"$file")
    
    # Loop through each line and process it
   while IFS= read -r line; do
      # Process each line individually (for example, print it)
   province=$(echo "$line" | sed -e 's/[^[:print:]]//g') #Remember to remove all hidden part of the line
   python src/weather_website_crawler/Timeanddate_crawler.py --province_name=$province --days=1 #Crawl province data with the max duration is 1 day
   done <<< "$content"
else
   echo "Error: Unable to read file $file"
fi
python src/weather_website_crawler/preprocessing_data.py --website_name=timeanddate.com --decode_weather_code=False
# python src/weather_website_crawler/import_csv_to_mongodb.py --website_name=timeanddate.com 
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.