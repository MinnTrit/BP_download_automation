# Sample video
[https://github.com/MinnTrit/BP_download_automation/assets/151976884/ee47184a-78f5-40bd-a2f3-97f8165410b2
](https://github.com/MinnTrit/BP_download_automation/assets/151976884/7dd9caa3-b52a-4217-b3eb-14c5d8e47f8f
)

# Overall diagram
![image](https://github.com/MinnTrit/BP_download_automation/assets/151976884/fc622b56-d8d6-482b-9f6f-004a1100cc18)

# Diagram's breakdown
```Notes```: This pipeline can be further implemented to the front-end through web framework in Python such as Django or Flask in order to trigger the code in the more user-friendly ways. At that time, we can run the code with ```headless = True``` option in PlayWright and use the proxy provided by ```Brightdata``` to help Playwright entered the website peacefully with the account

Equivalent tools to business's real case:
- Discord can be replaced with Slack or Microsoft Teams
- Google Drive can be replaced with Dropbox
### Workflow:
1. Requests made by the users: When the users request to the website, he/she will need to provide the ```sellers_id```, ```start_date```, and ```end_date``` parameters to launch the job
2. ```Automate.py``` received the request and prepare input: As the scrapper receives the parameter, it will perform these following actions:
   * For the ```start_date``` and ```end_date``` parameters, it will generate the date list within the range of the starting date and ending date for the scrapper
   * For the ```seller_id``` parameters it will find the according ```seller_name``` and ```seller_type``` of that seller to filter out the pannel on the website
3. ```Discord_bot.py``` prints the launched log in the server: After the prepared input has been made, the ```Discord_bot.py``` will receive outputs to launch the logs
4. ```Automate.py``` starts scrapping to save the file to the ```Temporary``` folder and concat the file to the dataframe: After the file being downloaded and stored in this folder, the contents of the file will be stored in the dataframe to be saved in the database later
5. ```Automate.py``` passes the file to ```Upload.py``` to store back-up files: After storing the file in the dataframe, the scrapper will pass this file to ```Upload.py``` so that it can use this file and upload to Google Drive for storage, after the file has been uploaded, ```Upload.py``` will also remove this file within the ```Temporary``` folder to clean up
6. ```Save.py``` starts saving the data to the database after all files have been downloaded: The ```Save.py``` will use the final dataframe of the scrapper and save the files' contents to the according table within the database
7. ```Save.py``` passes the total appended rows to ```Discord_bot.py``` for logs output: After all records have been saved, the ```Discord_bot.py``` will finally receive the total rows saved in the database to print the output logs
