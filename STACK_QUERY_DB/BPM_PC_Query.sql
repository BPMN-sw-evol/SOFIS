CREATE TABLE STACK_QUERY (
   id_discussion SERIAL PRIMARY KEY,
   title VARCHAR(255),
   link VARCHAR(255),
   score INTEGER,
   answer_count INTEGER,
   view_count INTEGER,
   creation_date DATE,
   tags VARCHAR(255)
);
select * from STACK_QUERY where title ilike '%camunda%';
truncate table BPM_PC_QUERY;
drop table BPM_PC_QUERY;