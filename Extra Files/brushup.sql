Drop table user;
Drop table employees;
Drop table jobreport;
Drop table jobinvoice;


 create table user(
    ID int auto_increment,
    username varchar(20) not null default '',
    password varchar(20) not null,
    Security_question_one varchar(20) not null,
	Security_question_two varchar(20) not null,
    constraint User_PK primary key(ID));
      
      ALTER TABLE user AUTO_INCREMENT=100;
    
    
    create table employees(
    employee_id  int auto_increment,
    ID int,
    first_name varchar(10),
    Middle_initial  varchar(1),
	last_name varchar(20),
    email varchar(20) not null,
   Phone_number varchar(12) not null,
	job_title  varchar(20) not null,
    password varchar(20) not null,
	 constraint employee_PK primary key(employee_id),
     constraint ID foreign key(ID) references user(ID));
      ALTER TABLE employees AUTO_INCREMENT=100;


Create Table jobreport(
jobid int auto_increment,
ID int,
customer_name varchar(20) not null,
Customer_address varchar(100) not null,
Job_description varchar(1000) not null,
jobCost int(10) not null,
jobDate date not null,
constraint jobreport_PK primary key(jobid),
constraint ID_FK  foreign key(ID) references User(ID));



 ALTER TABLE jobreport AUTO_INCREMENT=10001;
    


Create Table jobinvoice(
	invoiceid int auto_increment,
	jobid int,
	services_description varchar(1000) not null,
	materials_cost int(10) not null,
	labor_cost int(10) not null,
	total_cost int(10) not null,
	primary key (invoiceid),
	foreign key (jobid) references jobreport (jobid));

alter table jobInvoice auto_increment=1;
