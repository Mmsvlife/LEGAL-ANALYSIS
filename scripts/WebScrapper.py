import time
import re
import requests
from bs4 import BeautifulSoup
import csv

'''
https://apps.calbar.ca.gov/attorney/LicenseeSearch/AdvancedSearch?LastNameOption=b&LastName=&FirstNameOption=b&FirstName=&MiddleNameOption=b&MiddleName=&FirmNameOption=b&FirmName=&CityOption=c&City=Los+Angeles&State=CA&Zip=&District=&County=&LegalSpecialty=&LanguageSpoken=&PracticeArea=
'''
base_url = "https://apps.calbar.ca.gov/attorney/LicenseeSearch/AdvancedSearch?LastNameOption=b&LastName=&FirstNameOption=b&FirstName=&MiddleNameOption=b&MiddleName=&FirmNameOption=b&FirmName=&CityOption=c&City=Los+Angeles&State=CA&Zip=&District=&County=&LegalSpecialty=&LanguageSpoken=&PracticeArea="

headers = {'User-Agent': 'Mozilla/5.0'}

# page = requests.get(base_url, headers=headers)
# soup = BeautifulSoup(page.content, 'html.parser')
# attorney_details = []
#
# # Example: Extract all the attorney details
# links = soup.find_all('a')
# for link in links:
#     if link.get('href') and link.get('href').startswith("/attorney/Licensee/Detail/"):
#         attorney_details.append(link.get('href'))

# print(attorney_details)

base_url = "https://apps.calbar.ca.gov"
extracted = 0

attorney_url = "https://apps.calbar.ca.gov/attorney/Licensee/Detail/197722"
attorney_page = requests.get(attorney_url, headers=headers)

# print(attorney_page.content)

# Assuming the HTML content is stored in a variable called 'html_content'
soup = BeautifulSoup(attorney_page.content, 'html.parser')

# # Extract Name from the title
# name = soup.title.text.strip().split('-')[0].strip()
#
# email_span = soup.find('span', id='e8')


emails = []
# Find the next span tag which should contain the email
checks = 0
while checks < 25:
    print('e' + str(checks))
    email_span = soup.find('span', id='e' + str(checks))
    # print(email_span)
    if email_span and 'href' in email_span.attrs:
        # Extract the email from the href attribute
        href = email_span['href']
        match = re.search(r'mailto:(.*)', href)
        if match:
            emails.append(match.group(1))
    # print(checks)
    checks += 1
#     email_span = soup.find('span', id='e8')
#     if email_span and 'href' in email_span.attrs:
#         # Extract the email from the href attribute
#         href = email_span['href']
#         match = re.search(r'mailto:(.*)', href)
#         if match:
#             emails.append(match.group(1))
#
# Print the extracted emails
for email in emails:
    print(email)



# # Open a CSV file to write the results
# with open('results.csv', 'w', newline='') as csvfile:
#     csv_writer = csv.writer(csvfile)
#     csv_writer.writerow(['Name', 'Email'])  # Write header
#
#     for attorney in attorney_details:
#         if extracted == 10:
#             break
#         attorney_url = base_url + attorney
#         attorney_page = requests.get(attorney_url, headers=headers)
#
#         # Assuming the HTML content is stored in a variable called 'html_content'
#         soup = BeautifulSoup(attorney_page.content, 'html.parser')
#
#         # Extract Name from the title
#         name = soup.title.text.strip().split('-')[0].strip()
#
#         email_span = soup.find('span', id='e8')
#
#         emai_id = ''
#         if email_span:
#             text_content = str(email_span)
#             text_content = text_content.replace('&amp;', '&').replace('&#64;', '@')
#
#             # Remove any remaining HTML tags
#             email_id = re.sub(r'<[^>]+>', '', text_content)
#
#         print(name, email_id)
#         extracted += 1
#
#
#         # Write the result to the CSV file
#         csv_writer.writerow([name, email_id])
#
#         # If we've processed 10 items, sleep for 10 seconds
#         if extracted % 5 == 0:
#             print(f"Processed 5 items. Sleeping for 10 seconds...")
#             time.sleep(10)
#
#         if extracted >= 20:
#             break

print("Processing complete. Results saved to results.csv")
