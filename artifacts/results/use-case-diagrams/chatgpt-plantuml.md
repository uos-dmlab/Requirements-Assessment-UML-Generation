# ChatGPT PlantUML — Use Case Diagram Results

Generated using ChatGPT web interface (chatgpt.com) with GPT-5.2 Thinking, prompted: "Generate PlantUML code for a use case diagram based on these requirements. Return only the code between @startuml and @enduml." Code was then rendered via plantuml.com.

## TC11: ATM: ATM System

### PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Bank Customer" as Customer
actor "ATM Admin" as Admin
actor "Bank System" as Bank
rectangle "ATM" {
usecase "Authenticate (Enter PIN)" as UC_Auth
usecase "Check Balance" as UC_Balance
usecase "Withdraw Cash" as UC_Withdraw
usecase "Deposit Money" as UC_Deposit
usecase "Transfer Funds" as UC_Transfer
usecase "Refill Cash" as UC_Refill
usecase "View Transaction History" as UC_History
usecase "Validate Transaction" as UC_Validate
usecase "Update Account Balances" as UC_Update
}
Customer --> UC_Balance
Customer --> UC_Withdraw
Customer --> UC_Deposit
Customer --> UC_Transfer
Admin --> UC_Refill
Admin --> UC_History
UC_Balance --> UC_Auth : <<include>>
UC_Withdraw --> UC_Auth : <<include>>
UC_Deposit --> UC_Auth : <<include>>
UC_Transfer --> UC_Auth : <<include>>
UC_Refill --> UC_Auth : <<include>>
UC_History --> UC_Auth : <<include>>
UC_Balance --> UC_Validate : <<include>>
UC_Withdraw --> UC_Validate : <<include>>
UC_Deposit --> UC_Validate : <<include>>
UC_Transfer --> UC_Validate : <<include>>
UC_Withdraw --> UC_Update : <<include>>
UC_Deposit --> UC_Update : <<include>>
UC_Transfer --> UC_Update : <<include>>
Bank --> UC_Validate
Bank --> UC_Update
Bank --> UC_History
@enduml
```

### Generated Diagram

![TC11_ATM - ChatGPT PlantUML](../images/usecase/chatgpt/TC11_ATM.png)

---

## TC12: OnlineStore: Online Store

### PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Customer" as Customer
actor "Admin User" as Admin
actor "Payment Provider" as PSP
rectangle "Online Store Website" {
usecase "Log In" as UC_Login
usecase "Browse Products" as UC_Browse
usecase "Search by Category" as UC_SearchCategory
usecase "Add Item to Cart" as UC_AddToCart
usecase "Checkout" as UC_Checkout
usecase "Track Order" as UC_TrackOrder
usecase "Process Payment" as UC_Payment
usecase "Manage Inventory" as UC_Inventory
usecase "Handle Refunds" as UC_Refunds
usecase "View Sales Reports" as UC_Reports
}
Customer --> UC_Browse
Customer --> UC_SearchCategory
Customer --> UC_AddToCart
Customer --> UC_Checkout
Customer --> UC_TrackOrder
UC_Checkout --> UC_Login : <<include>>
UC_AddToCart --> UC_Login : <<include>>
UC_Checkout --> UC_Payment : <<include>>
PSP --> UC_Payment
Admin --> UC_Inventory
Admin --> UC_Refunds
Admin --> UC_Reports
@enduml
```

### Generated Diagram

![TC12_OnlineStore - ChatGPT PlantUML](../images/usecase/chatgpt/TC12_OnlineStore.png)

---

## TC13: Library: Library System

### PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Member" as Member
actor "Librarian" as Librarian
rectangle "Library System" {
usecase "Register Member" as UC_Register
usecase "Authenticate Member" as UC_Auth
usecase "Search Books" as UC_Search
usecase "Place Hold on Book" as UC_Hold
usecase "Borrow Book" as UC_Borrow
usecase "Return Book" as UC_Return
usecase "Add New Book" as UC_AddBook
usecase "Remove Book" as UC_RemoveBook
usecase "Manage Member Accounts" as UC_ManageMembers
usecase "Handle Late Fees" as UC_LateFees
usecase "Send Reservation Notification" as UC_Notify
}
Member --> UC_Search
Member --> UC_Hold
Member --> UC_Borrow
Member --> UC_Return
Member --> UC_Register
UC_Borrow --> UC_Auth : <<include>>
UC_Hold --> UC_Auth : <<include>>
Librarian --> UC_AddBook
Librarian --> UC_RemoveBook
Librarian --> UC_ManageMembers
Librarian --> UC_LateFees
UC_Hold --> UC_Notify : <<include>>
@enduml
```

### Generated Diagram

![TC13_Library - ChatGPT PlantUML](../images/usecase/chatgpt/TC13_Library.png)

---

## TC14: Hospital: Hospital Appointment

### PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Patient" as Patient
actor "Doctor" as Doctor
actor "Receptionist" as Receptionist
actor "Billing System" as Billing
rectangle "Hospital Appointment System" {
usecase "Sign Up" as UC_SignUp
usecase "Authenticate User" as UC_Auth
usecase "View Available Time Slots" as UC_ViewSlots
usecase "Book Appointment" as UC_Book
usecase "Cancel Appointment" as UC_Cancel
usecase "Check Schedule" as UC_CheckSchedule
usecase "Mark Appointment as Completed" as UC_MarkDone
usecase "Manage Calendar" as UC_ManageCalendar
usecase "Register Walk-in Patient" as UC_WalkIn
usecase "Send Appointment Reminder" as UC_Reminder
usecase "Process Payment" as UC_Payment
}
Patient --> UC_SignUp
Patient --> UC_ViewSlots
Patient --> UC_Book
Patient --> UC_Cancel
UC_Book --> UC_Auth : <<include>>
UC_Cancel --> UC_Auth : <<include>>
Doctor --> UC_CheckSchedule
Doctor --> UC_MarkDone
Receptionist --> UC_ManageCalendar
Receptionist --> UC_WalkIn
Receptionist --> UC_Reminder
UC_Book --> UC_Payment : <<include>>
Billing --> UC_Payment
@enduml
```

### Generated Diagram

![TC14_Hospital - ChatGPT PlantUML](../images/usecase/chatgpt/TC14_Hospital.png)

---

## TC15: ELearning: E-Learning Platform

### PlantUML Code

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
actor "Student" as Student
actor "Teacher" as Teacher
actor "Admin" as Admin
rectangle "Online Learning Platform" {
usecase "Browse Courses" as UC_Browse
usecase "Enroll in Course" as UC_Enroll
usecase "Watch Course Videos" as UC_Watch
usecase "Submit Homework" as UC_SubmitHW
usecase "Take Quiz" as UC_TakeQuiz
usecase "Receive Certificate" as UC_Certificate
usecase "Create Course" as UC_CreateCourse
usecase "Upload Course Materials" as UC_Upload
usecase "Grade Assignments" as UC_Grade
usecase "Post Announcement" as UC_Announce
usecase "Manage User Accounts" as UC_ManageUsers
usecase "Approve Course" as UC_ApproveCourse
usecase "Monitor Platform Usage" as UC_Monitor
usecase "Validate Course Completion" as UC_ValidateCompletion
}
Student --> UC_Browse
Student --> UC_Enroll
Student --> UC_Watch
Student --> UC_SubmitHW
Student --> UC_TakeQuiz
Student --> UC_Certificate
Teacher --> UC_CreateCourse
Teacher --> UC_Upload
Teacher --> UC_Grade
Teacher --> UC_Announce
Admin --> UC_ManageUsers
Admin --> UC_ApproveCourse
Admin --> UC_Monitor
UC_CreateCourse --> UC_ApproveCourse : <<include>>
UC_Certificate --> UC_ValidateCompletion : <<include>>
@enduml
```

### Generated Diagram

![TC15_ELearning - ChatGPT PlantUML](../images/usecase/chatgpt/TC15_ELearning.png)

---
