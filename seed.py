import json
from datetime import datetime
from zoneinfo import ZoneInfo
from app.database import SessionLocal, engine
from app.models import Writing, Certificate, Comment, Experience, Base

blogs = [
	{
		"title": "Grateful for the journey at LG Sinarmas Technology Solutions (LGSM) as part of the Smart Factory Development Team.",
        "content": "Grateful for the journey at LG Sinarmas Technology Solutions (LGSM) as part of the Smart Factory Development Team.\n\nSince joining on December 9, 2024, I had the opportunity to contribute to EV Battery Smart Factory initiatives, working on backend systems that support core MES (Manufacturing Execution System) operations and workflows\n\nAlong the way, I was also involved in analyzing production data, validating backend features to ensure performance and reliability, and developing internal applications to support recruitment processes within LG Sinarmas Technology Solutions.\n\nToday (December 26, 2025) marks the end of this chapter. I’m proud of the work delivered, the systems built, and the lessons learned from an incredible team.\n\nThank you to everyone I had the chance to work with. Wishing LGSM and the Smart Factory team continued success ahead.✨",
		"date": "Dec 27, 2025",
		"author": "Abdul Mannan Saipi",
		"authorImg": "/static/img/author/abdulmannansaipi.png",
		"image": "https://media.licdn.com/dms/image/v2/D5622AQF3bv7cJC4TIg/feedshare-shrink_1280/B56Ztbk0ntKcAs-/0/1766767967176?e=1784764800&v=beta&t=LfU8TlZCEyrU14yoF1E--orIgim05fJG8Yw6zN6k8iA",
        "images": [
            "https://media.licdn.com/dms/image/v2/D562DAQEjRjOOdOJmCQ/profile-treasury-image-shrink_1280_1280/B56ZWHE3ywGUAQ-/0/1741727980319?e=1783868400&v=beta&t=-_2t1uMo6HEnZ_J56Dxp96No1KG63jZ4MbKJbZuWkAY",
            "https://media.licdn.com/dms/image/v2/D562DAQEn2DAKojkkrw/profile-treasury-image-shrink_1280_1280/profile-treasury-image-shrink_1280_1280/0/1737023600328?e=1783868400&v=beta&t=Yt9OxVj6wN49F_BHhKocGEUFe1So14QytQ4brZ-LeNU",
			"https://media.licdn.com/dms/image/v2/D562DAQE81nvkfXqqMA/profile-treasury-image-shrink_1280_1280/profile-treasury-image-shrink_1280_1280/0/1737023658186?e=1783868400&v=beta&t=xVrzEjo1dnKYYTvlfI2xNs9XI9091vJTmLXCQDJBZKI",
        ]
	},
	{
		"title": "Reflecting on an Incredible Internship Journey at Mattel",
        "content": "🌟 Reflecting on an Incredible Internship Journey at Mattel 🌟\n\nYesterday, December 6th, marked the end of an incredible chapter in my professional journey—my internship at Mattel, which began on January 3rd, 2024. Over the past 11 months, I had the privilege of working with an amazing team in the EHS & Compliance Department, learning from industry experts, and contributing to exciting projects that challenged me to grow both personally and professionally.\n\nFrom developing innovative solutions to collaborating on impactful initiatives, my time at Mattel has been nothing short of transformative. I am deeply grateful for the support and guidance I received from my mentors, colleagues, and everyone who made this experience so enriching.\n\nA special thank you to the EHS & Compliance team for fostering such a collaborative and inspiring environment. I’ve gained invaluable skills, built lasting connections, and discovered new perspectives that I will carry with me throughout my career.\n\nAlthough this chapter has come to an end, I’m excited for what lies ahead as I continue to build on the foundation I’ve established here.\n\nTo my fellow interns and colleagues—thank you for making this journey unforgettable. Let’s stay connected, and I look forward to seeing all the amazing things you’ll achieve!\n\n#EndOfAnEra #MattelInternship #EHSTeam #Grateful #LearningAndGrowth",
		"date": "Dec 07, 2024",
		"author": "Abdul Mannan Saipi",
		"authorImg": "/static/img/author/abdulmannansaipi.png",
		"image": "https://media.licdn.com/dms/image/v2/D5622AQFkxwoPux7gEg/feedshare-shrink_1280/feedshare-shrink_1280/0/1733557069514?e=1784764800&v=beta&t=tAPL65CU2l3iwbxKDGlpxh378i_xDdjJXKr3BfCgCz0",
        "images": [
			"https://media.licdn.com/dms/image/v2/D5622AQFkxwoPux7gEg/feedshare-shrink_1280/feedshare-shrink_1280/0/1733557069514?e=1784764800&v=beta&t=tAPL65CU2l3iwbxKDGlpxh378i_xDdjJXKr3BfCgCz0",
			"https://media.licdn.com/dms/image/v2/D5622AQH2lQAYPl33rQ/feedshare-shrink_800/feedshare-shrink_800/0/1733557069584?e=1784764800&v=beta&t=5TpzkPJVxw-YiX56wfTiKqlYcKrHlLNOJL4y65DkprU",
			"https://media.licdn.com/dms/image/v2/D5622AQGjQbNdxfSHig/feedshare-shrink_800/feedshare-shrink_800/0/1733557067969?e=1784764800&v=beta&t=tvgIgYSBTLFFpdVeGD0YfURZwpyV4BRn3-zYVrGc5Us"

        ]
	}
]

certificates = [
	{
		"name": "Bangkit Academy led by Google, Tokopedia, Gojek, & Traveloka",
		"year": "2023",
		"desc": "Bangkit Academy is a bootcamp led by major tech companies in Indonesia and is part of the Kampus Merdeka program.",
		"img": "/static/img/certificates/bangkit.png",
		"bgColor": "bg-gray-500",
		"link": "https://drive.google.com/file/d/13mgCEnwhO1DTpc7c_z0Fs8cNt-BHrBR4/view?usp=sharing",
	},
	{
		"name": "The Bits and Bytes of Computer Networking",
		"year": "2023",
		"desc": "I learned about different types of networks, how data travels across the internet, the OSI and TCP/IP models, network hardware like routers and switches, IP addressing, DNS, and troubleshooting tools. ",
		"img": "/static/img/certificates/coursera1.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.coursera.org/account/accomplishments/certificate/W7HL5ZKJY2JY",
	},
	{
		"name": "System Administration and IT Infrastructure Services",
		"year": "2023",
		"desc": "I learned how to set up system services, manage security, and ensure the smooth operation of IT environments,",
		"img": "/static/img/certificates/coursera2.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.coursera.org/account/accomplishments/certificate/SASKPNKXVL54",
	},
	{
		"name": "Clean Code",
		"year": "2025",
		"desc": "This course taught me the principles of writing clean, readable, and maintainable code including refactoring, naming conventions, and SOLID principles.",
		"img": "/static/img/certificates/cleancode.jpg",
		"bgColor": "bg-gray-500",
		"link": "https://www.udemy.com/certificate/UC-cb95c7f8-4a41-4553-88f9-b8309617bd59",
	},
	{
		"name": "Data Structures & Algorithms",
		"year": "2025",
		"desc": "I learned how to solve coding problems using data structures like linked lists, trees, and graphs, and algorithms such as sorting, recursion, and dynamic programming.",
		"img": "/static/img/certificates/dsa.jpg",
		"bgColor": "bg-gray-500",
		"link": "https://www.udemy.com/certificate/UC-402b38d3-d4a7-4fd1-95b2-79d6ecea97b2",
	},
	{
		"name": "React Developer Course",
		"year": "2025",
		"desc": "I learned the fundamentals of React, including creating components, managing state and props, using JSX, and applying effects and context.",
		"img": "/static/img/certificates/react.jpg",
		"bgColor": "bg-gray-500",
		"link": "https://www.udemy.com/certificate/UC-c9c96781-c93f-4a13-84f7-9090bd3a1384",
	},
	{
		"name": "SQL & Database Management",
		"year": "2025",
		"desc": "I learned how to design and manage relational databases using Microsoft SQL Server. I practiced writing SQL queries (CRUD), creating tables, views, stored procedures, and managing users, backups, and security.",
		"img": "/static/img/certificates/sql.jpg",
		"bgColor": "bg-gray-500",
		"link": "https://www.udemy.com/certificate/UC-5c1cea8a-a851-4e5c-91c1-23eb1217230d",
	},
	{
		"name": "Java Programming",
		"year": "2025",
		"desc": "I learned the basics of Java programming, including variables, loops, methods, conditionals, and object-oriented programming (OOP).",
		"img": "/static/img/certificates/java.jpg",
		"bgColor": "bg-gray-500",
		"link": "https://www.udemy.com/certificate/UC-0cf7996f-5eb2-4835-ab45-541329091aba",
	},
	{
		"name": "Build Back-End Applications with Google Cloud",
		"year": "2023",
		"desc": "I learned the basics of back-end development, Node.js, creating RESTful APIs, deploying them on Google Compute Engine, and testing them with Postman.",
		"img": "/static/img/certificates/dicoding2.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.dicoding.com/certificates/ERZR0QE5NXYV",
	},
	{
		"name": "Become a Google Cloud Engineer",
		"year": "2023",
		"desc": "I learned the basics of cloud computing with Google Cloud, including how to build, manage, and monitor cloud apps through hands-on practice and a final project.",
		"img": "/static/img/certificates/dicoding1.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.dicoding.com/certificates/1RXY6O233ZVM",
	},
	{
		"name": "JavaScript Programming",
		"year": "2023",
		"desc": "I learned concepts like variables, loops, data structures (e.g., Arrays, Objects), functions, and object-oriented programming (OOP). The course also covers asynchronous programming, error handling, and working with Node.js",
		"img": "/static/img/certificates/dicoding3.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.dicoding.com/certificates/6RPN6LE38P2M",
	},
	{
		"name": "Web Development",
		"year": "2023",
		"desc": "The course covers creating web page structure with HTML and enhancing web page appearance with CSS. It also includes learning advanced CSS techniques, responsive design with Flexbox, and building a simple website project.",
		"img": "/static/img/certificates/dicoding4.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.dicoding.com/certificates/1OP8587JQPQK",
	},
	{
		"name": "Google Cloud Skill Boost",
		"year": "2023",
		"desc": "I’ve earned several Google Cloud Skills Boost badges. Some of the badges include Kubernetes, Cloud Run, and hybrid cloud applications. I also completed courses on Google Cloud fundamentals, Terraform, networking, security, and machine learning APIs.",
		"img": "/static/img/certificates/gcsb.png",
		"bgColor": "bg-gray-500",
		"link": "https://www.cloudskillsboost.google/public_profiles/5d03fd6c-a138-4e59-b072-85c1174c5051",
	},
]

comments = [
    {
        "name": "John Doe",
        "date": "Apr 5, 2025",
        "comment": "Lorem ipsum dolor sit amet consectetur, adipisicing elit. Ex eos ipsam laudantium minus debitis neque iste autem alias eius distinctio.",
        "totalLikes": 83,
        "profileImg": "/static/img/author/no_profile.jpeg",
    },
    {
        "name": "Win Dev",
        "date": "July 25, 2029",
        "comment": "Lorem ipsum dolor. Ex eos ipsam laudantium minus debitis neque iste autem alias eius distinctio.",
        "totalLikes": 99,
        "profileImg": "/static/img/author/no_profile.jpeg",
    },
]

works = [
	{
		"company": "Samsung R&D Indonesia",
		"role": "Software Engineer",
		"desc": "Since December 2025, I've been working at Samsung Research & Development Indonesia",
		"startDate": "Dec 2025",
		"endDate": "Present",
		"img": "/static/img/profiles/SAMSUNG.jpg",
		"points": [],
		"iamges": [],
		"bgColor": "bg-gray-100",
		"url": "",
	},
	{
		"company": "LG Sinar Mas",
		"role": "Software Engineer",
		"desc": "From December 2024 to December 2025, I've been working as a Software Engineer at LG Sinar Mas Technology Solutions, where I contribute to the development of smart factory systems for EV (Electric Vehicle) battery manufacturing across multiple countries.",
		"startDate": "Dec 2024",
		"endDate": "Dec 2025",
		"img": "/static/img/profiles/galadinerlgsm.JPEG",
		"points": [
			"Contributed to the development of smart factory systems for EV battery manufacturing across multiple countries such as South Korea, the United States, China, Poland, and Indonesia.",
			"Designed and maintained backend logic to support core MES (Manufacturing Execution System) operations, ensuring seamless and accurate production workflows.",
			"Analyze production data and validate backend features to ensure performance, reliability, and data accuracy.",
			"Developed job portal and job posting applications for LG Sinarmas Technology Solutions to streamline recruitment processes.",
		],
		"iamges": ["/static/img/profiles/lg1.jpeg", "/static/img/profiles/lg2.jpeg"],
		"bgColor": "bg-neutral-800",
		"url": "",
	},
	{
		"company": "PT. \u00A0Mattel Indonesia",
		"role": "Full Stack Developer",
		"desc": "From January to December 2024, I worked as a Full Stack Developer at Mattel Indonesia for 1 year, focusing on building internal systems and improving operational efficiency.",
		"startDate": "Jan 2024",
		"endDate": "Dec 2024",
		"img": "/static/img/profiles/mattel.jpg",
		"points": [
			"I led the digital transformation of manual processes by developing systems like Audit Process, Reporting, Waste Management, Compliance Monitoring, Incident Reporting, and Inventory Management using ASP.NET, Power Apps, and SQL Server.",
			"Maintained and managed databases with SQL Server and visualized data through Power BI; used Power Automate and Gateway for streamlined workflows and secure access.",
			"Recognized as a semi-finalist (Top 8) in the Global Manufacturing Internship Competition for innovative and impactful contributions.",
			"Collaborated with cross-functional teams to turn business requirements into efficient technical solutions, receiving praise for innovation and problem-solving.",
		],
		"iamges": ["/static/img/profiles/mattel2.jpeg", "/static/img/profiles/mattel1.jpeg"],
		"bgColor": "bg-neutral-400",
		"url": "",
	},
	{
		"company": "Sekretariat Jendral DPR RI",
		"role": "IT Programmer",
		"desc": "Interned at Sekretariat Jendral DPR RI for 5 months through the Kampus Merdeka program, working on data visualization tools and system architecture for legal data management.",
		"startDate": "Aug 2023",
		"endDate": "Dec 2023",
		"img": "/static/img/profiles/dpr.JPEG",
		"points": [
			"Developed a data visualization dashboard similar to Tableau/Power BI using Laravel and SQL, allowing users to create customizable charts and layouts for personalized analysis.",
			"Built an efficient data scheduler with Node.js that periodically pulls optimized datasets from the main database, significantly improving load times and performance.",
			"Designed the improvement system of the 'Dashboard Website Program Legislasi Nasional DPR', including architecture planning, use case diagrams, activity diagrams, and ERDs to improve legal data management and website accountability.",
		],
		"iamges": ["/static/img/profiles/dpr1.jpeg", "/static/img/profiles/dpr2.jpeg"],
		"bgColor": "bg-zinc-700",
		"url": "",
	},
]

def get_wib_time():
    return datetime.now(ZoneInfo("Asia/Jakarta"))

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(Comment).delete()
        db.query(Writing).delete()
        db.query(Certificate).delete()
        db.query(Experience).delete()
        
        # 1. Seed Blogs (Writings)
        writing_objects = []
        for i, b in enumerate(blogs, 1):
            pub_date = datetime.strptime(b["date"], "%b %d, %Y").replace(tzinfo=ZoneInfo("Asia/Jakarta"))
            writing = Writing(
                title=b["title"],
                content=b.get("content", ""), 
                published_at=pub_date,
                author=b["author"],
                author_img=b["authorImg"],
                image=b["image"],
                images=json.dumps(b.get("images", [])),
                order=i
            )
            db.add(writing)
            writing_objects.append(writing)
            
        db.commit()
        
        # 2. Seed Certificates
        for i, c in enumerate(certificates, 1):
            cert = Certificate(
                name=c["name"],
                year=c["year"],
                description=c["desc"],
                img=c["img"],
                bg_color=c["bgColor"],
                link=c["link"],
                order=i
            )
            db.add(cert)
            
        # 3. Seed Works (Experiences)
        for i, w in enumerate(works, 1):
            exp = Experience(
                company=w["company"],
                position=w["role"],
                start_date=w["startDate"],
                end_date=w["endDate"],
                description=w["desc"],
                img=w["img"],
                points=json.dumps(w["points"]),
                images=json.dumps(w["iamges"]), # Keeping original typo keys
                bg_color=w["bgColor"],
                url=w["url"],
                order=i
            )
            db.add(exp)
            
        db.commit()
        
        # 4. Seed Comments
        # We'll attach the provided comments to the first blog
        if writing_objects:
            first_writing = writing_objects[0]
            for c in comments:
                created_date = datetime.strptime(c["date"], "%b %d, %Y").replace(tzinfo=ZoneInfo("Asia/Jakarta")) if "date" in c and c["date"] != "July 25, 2029" else get_wib_time() 
                # Fixing the date parsing for "July 25" which doesn't match "%b" easily without careful handling
                if c["date"] == "July 25, 2029":
                    created_date = datetime.strptime("Jul 25, 2029", "%b %d, %Y").replace(tzinfo=ZoneInfo("Asia/Jakarta"))
                
                comment = Comment(
                    writing_id=first_writing.id,
                    username=c["name"],
                    content=c["comment"],
                    profile_img=c["profileImg"],
                    likes=c["totalLikes"],
                    is_author=(c["name"] == "Abdul Mannan Saipi"),
                    created_at=created_date
                )
                db.add(comment)
        
        db.commit()
        print("Successfully seeded the database!")
        
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
