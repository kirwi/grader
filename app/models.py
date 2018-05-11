from app import graph, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from py2neo.ogm import GraphObject, Property, RelatedFrom, RelatedTo
from hashlib import md5
from datetime import datetime

class Assignment(GraphObject):
    __primarykey__ = 'title'

    type = Property()
    title = Property()
    points = Property()
    date_created = Property()
    due_date = Property()

    @classmethod
    def find(cls, title):
        return cls.select(graph, title).first()

    def add_to_db(self, email, score):
        add_query = """
        MATCH (s:Student {email: {email}})-[r:SCORED]->(a:Assignment {title: {title}})
        SET r.score = {score}
        """
        graph.run(add_query, email=email, score=score, title=self.title)

class User(GraphObject, UserMixin):
    __primarykey__ = 'email'

    email = Property()
    password = Property()
    user_id = Property()
    name = Property()
    role = Property()

    def get_courses(self):
        course_query = """
        MATCH (u {email: {email}})<-[]-(c:Course)
        RETURN c.description AS description, c.term AS term,
        c.section AS section, c.title AS title, c.year AS year
        """
        return graph.run(course_query, email=self.email)

    def get_id(self):
        return self.email

    def set_password(self, password):
        self.password = generate_password_hash(password)
        graph.push(self)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size
        )

    # Used to separate the model graph from the implementation. I don't want
    # to import the graph into the code in other places of the app.
    @classmethod
    def find(cls, email):
        return cls.select(graph, email).first()

class Course(GraphObject):
    __primarykey__ = 'section'

    title = Property()
    section = Property()
    description = Property()
    term = Property()
    year = Property()

    students = RelatedTo('User', 'IS_ENROLLED')
    instructors = RelatedTo('User', 'IS_INSTRUCTOR')

    def get_grades(self):
        grades_query = """
        MATCH (:Course {{section: {section}}})-[:IS_ENROLLED]->(s:Student)-[r:SCORED]->(a:Assignment)
        WITH {{name: s.name, email: s.email}} AS student, collect({{assignment: a, score: r.score}}) AS assignments
        RETURN student, assignments
        ORDER BY student['name']
        """.format(section=self.section)
        return graph.run(grades_query)

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

    def add_assignment(self):
        pass

    @classmethod
    def find(cls, section):
        return cls.select(graph, section).first()

@login.user_loader
def load_user(email):
    return User.find(email)
