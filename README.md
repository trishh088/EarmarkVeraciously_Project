# EarmarkVeraciously Project
This project was created as a final project for IST 659 - Data Administration Concepts and Database Management at Syracuse University for MS in Applied Data Science Degree.

## Motivation for the project:
The whole idea behind this project was to make it easier for students to track how much they are spending on shared expenses along with their individual expenses.

## Components of the project:
1. Docker was used for creating a containerized application to host the database application locally.
2. Azure Recognizer services were used for OCR (Optical Character Recognition) and AI (Artificial Intelligence) technology to scan receipts and extract details such as vendor name, item name, total expense, vendor address etc.
3. A SQL script was created to build the database and the tables needed to capture the billing information. The conceptual and ERD documents are attached in the git repository to understand how the database was built.
4. A Python script was created to connect to both the Azure Recognizer API and the database to check if the details of the bill already exist in the database and in case there is no entry then the script enters the details into the database.
5. A log file was created to validate if the entries that are being made to the database are correct or not for users to manually validate if needed.
6. Finally the database was connected to the Power BI application to create monthly reports to track expenses as needed.
