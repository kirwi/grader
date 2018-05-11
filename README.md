# Grader

Grader is an open source course management system. I started this project
as an adjunct community college professor in an attempt to provide students
with grade feedback, and to manage several courses I was teaching at once.
It is inspired by popular, commercially available content management
applications like Blackboard and Canvas.

## Student and instructor users

Grader's data and relationships are powered by a neo4j graph database. Students,
instructors, courses, assignments, etc. are all stored as nodes in the graph.
Then relationships (graph edges) are formed between various nodes which may
carry additional information about a particular relationship. For example,
both student and instructor users derive from a base user model with the
following node properties: **email, password, user_id, name, role**. An
assignment node has properties: **type, title, points, date_created, due_date**.
A student's grade on a particular assignment is stored in the relationship
property linking the student with the assignment:

`(s:Student)-[r:SCORED {score: 34}]->(a:Assignment)`

## Retrieving information

The `Course` class contains methods for returning queries about students,
instructors, and assignments. This is achieved with a mixture of built in
functionality of py2neo's Object Graphical Mapper, and pure Cypher queries. For
example, the OGM makes it easy to get a list of all the `Course` nodes related
to `Student` nodes via a `IS_ENROLLED` relationship (list of enrolled students):

`students = RelatedTo('User', 'IS_ENROLLED')`

Obtaining a record of all the assignments for a particular course is achieved
with a method which implements a pure Cypher statement:

```python
def get_assignments(self):
      assignments_query = """
      MATCH (c:Course {{section: {section}}})-[:ASSIGNED]->(a:Assignment)
      WITH collect(a.type) AS types, c
      UNWIND types AS type
      MATCH (c)-[:ASSIGNED]->(a:Assignment {{type: type}})
      WITH a, type
      ORDER BY a.due_date
      RETURN type AS type, collect(a) AS assignments
      """.format(section=self.section)
      return graph.run(assignments_query)
```
