# UMLReq System — Use Case Diagram Results

Generated using GPT-4o (gpt-4o-2024-11-20) via OpenAI API with temperature=0.3, top_p=1.0, RAG grounding in PlantUML documentation, and methodology-aware prompts (Cockburn's goal-level taxonomy, Jacobson's actor classification).

## TC11: ATM: ATM System

### PlantUML Code

```plantuml
@startuml
left to right direction
actor "Bank Customer" as BC
actor "Admin" as AD
actor "Bank System" as BS <<system>>
rectangle "ATM System" {
usecase "Enter PIN" as UC1
usecase "Verify PIN" as UC2
usecase "Check balance" as UC3
usecase "Withdraw cash" as UC4
usecase "Deposit cash" as UC5
usecase "Transfer money between accounts" as UC6
usecase "Update balances" as UC7
usecase "Refill cash" as UC8
usecase "View transaction history" as UC9
}
BC --> UC1
UC1 ..> UC2 : <<include>>
UC2 --> BS
BC --> UC3
UC3 --> BS
BC --> UC4
UC4 --> BS
UC4 ..> UC7 : <<include>>
BC --> UC5
UC5 --> BS
UC5 ..> UC7 : <<include>>
BC --> UC6
UC6 --> BS
UC6 ..> UC7 : <<include>>
AD --> UC8
AD --> UC9
UC9 --> BS
@enduml
```

### Generated Diagram

![TC11_ATM - UMLReq System](../images/usecase/umlreq/TC11_ATM.png)

---

## TC12: OnlineStore: Online Store

### PlantUML Code

```plantuml
@startuml
left to right direction
actor Customer
actor Admin
actor "Third Party Payment System" <<system>>
rectangle "Online Store System" {
usecase "Browse products" as UC_Browse
usecase "Search products by category" as UC_Search
usecase "Add product to cart" as UC_AddCart
usecase "Checkout" as UC_Checkout
usecase "Track order status" as UC_TrackOrder
usecase "Log in" as UC_Login
usecase "Process payment" as UC_ProcessPayment
usecase "Manage stock" as UC_ManageStock
usecase "Handle refunds" as UC_HandleRefunds
usecase "Generate sales reports" as UC_GenerateReports
}
Customer --> UC_Browse
Customer --> UC_Search
Customer --> UC_AddCart
Customer --> UC_Checkout
Customer --> UC_TrackOrder
Customer --> UC_Login
UC_Checkout ..> UC_ProcessPayment : <<include>>
"Third Party Payment System" --> UC_ProcessPayment
Admin --> UC_ManageStock
Admin --> UC_HandleRefunds
Admin --> UC_GenerateReports
@enduml
```

### Generated Diagram

![TC12_OnlineStore - UMLReq System](../images/usecase/umlreq/TC12_OnlineStore.png)

---

## TC13: Library: Library System

### PlantUML Code

```plantuml
@startuml
left to right direction
actor "Member" as Member
actor "Librarian" as Librarian
rectangle "Library System" {
usecase "Search for books" as UC_Search
usecase "Put book on hold" as UC_Hold
usecase "Borrow book" as UC_Borrow
usecase "Return book" as UC_Return
usecase "Add new book" as UC_Add
usecase "Remove old book" as UC_Remove
usecase "Manage member account" as UC_Manage
usecase "Handle late fees" as UC_Fees
usecase "Notify member about reserved book availability" as UC_Notify
}
Member --> UC_Search
Member --> UC_Hold
Member --> UC_Borrow
Member --> UC_Return
Librarian --> UC_Add
Librarian --> UC_Remove
Librarian --> UC_Manage
Librarian --> UC_Fees
UC_Hold ..> UC_Notify : <<include>>
@enduml
```

### Generated Diagram

![TC13_Library - UMLReq System](../images/usecase/umlreq/TC13_Library.png)

---

## TC14: Hospital: Hospital Appointment

### PlantUML Code

```plantuml
@startuml
left to right direction
actor "Patient" as Patient
actor "Doctor" as Doctor
actor "Receptionist" as Receptionist
actor "Billing System" as BillingSystem <<system>>
rectangle "Hospital Appointment System" {
usecase "Sign up as patient" as UC_SignUp
usecase "View available times" as UC_ViewTimes
usecase "Book an appointment" as UC_Book
usecase "Cancel an appointment" as UC_Cancel
usecase "Check schedule" as UC_CheckSchedule
usecase "Mark appointment as done" as UC_MarkDone
usecase "Manage calendar" as UC_ManageCalendar
usecase "Sign up walk-in patient" as UC_SignUpWalkIn
usecase "Send appointment reminders" as UC_SendReminders
usecase "Process payment" as UC_ProcessPayment
}
Patient --> UC_SignUp
Patient --> UC_ViewTimes
Patient --> UC_Book
Patient --> UC_Cancel
Doctor --> UC_CheckSchedule
Doctor --> UC_MarkDone
Receptionist --> UC_ManageCalendar
Receptionist --> UC_SignUpWalkIn
Receptionist --> UC_SendReminders
UC_Book ..> UC_ProcessPayment : <<include>>
BillingSystem --> UC_ProcessPayment
@enduml
```

### Generated Diagram

![TC14_Hospital - UMLReq System](../images/usecase/umlreq/TC14_Hospital.png)

---

## TC15: ELearning: E-Learning Platform

### PlantUML Code

```plantuml
@startuml
left to right direction
actor "Student" as Student
actor "Teacher" as Teacher
actor "Admin" as Admin
rectangle "Online Learning Platform" {
usecase "Browse courses" as UC_BrowseCourses
usecase "Sign up for course" as UC_SignUp
usecase "Watch course videos" as UC_WatchVideos
usecase "Submit homework" as UC_SubmitHomework
usecase "Take quizzes" as UC_TakeQuizzes
usecase "Receive certificate for course completion" as UC_ReceiveCertificate
usecase "Create course" as UC_CreateCourse
usecase "Upload course materials" as UC_UploadMaterials
usecase "Grade student work" as UC_GradeWork
usecase "Post announcements" as UC_PostAnnouncements
usecase "Manage user accounts" as UC_ManageAccounts
usecase "Approve courses" as UC_ApproveCourses
usecase "Track platform usage" as UC_TrackUsage
}
Student --> UC_BrowseCourses
Student --> UC_SignUp
Student --> UC_WatchVideos
Student --> UC_SubmitHomework
Student --> UC_TakeQuizzes
Student --> UC_ReceiveCertificate
Teacher --> UC_CreateCourse
UC_CreateCourse ..> UC_UploadMaterials : <<include>>
Teacher --> UC_GradeWork
Teacher --> UC_PostAnnouncements
Admin --> UC_ManageAccounts
Admin --> UC_ApproveCourses
Admin --> UC_TrackUsage
@enduml
```

### Generated Diagram

![TC15_ELearning - UMLReq System](../images/usecase/umlreq/TC15_ELearning.png)

---
