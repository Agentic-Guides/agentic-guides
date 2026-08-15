#!/usr/bin/env python3
"""100ニッチのディレクトリサイトを自動生成・デプロイする。
60サイト（金融・税務・保険・投資）に被らないニッチを選定。
トークン消費を抑えるため、このスクリプトが全サイトを自動生成・デプロイする。
"""
import sys, os, subprocess, json, re
sys.path.insert(0, os.path.expanduser("~/Desktop/agentic-sites"))
from directory_builder import build_directory

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# 60サイトに無いニッチ100個（金融・税務・保険・投資を除外）
# 各ニッチ: (slug, name, description, kicker, カテゴリとリンク)
NICHES = [
    # ペット
    ("dog-care-directory", "Dog Care Directory", "Curated directory of dog care resources, training, health, and products.", "Find Dog Care & Training Resources", {
        "Dog Training": [{"title":"AKC Training","url":"https://www.akc.org/expert-advice/training/","desc":"American Kennel Club dog training guides."}],
        "Dog Health": [{"title":"Vetstreet","url":"https://www.vetstreet.com/","desc":"Veterinary health information for dogs."}],
    }),
    ("cat-care-directory", "Cat Care Directory", "Curated directory of cat care resources, health, and products.", "Find Cat Care & Health Resources", {
        "Cat Health": [{"title":"Cornell Feline Health","url":"https://www.vet.cornell.edu/","desc":"Cornell University feline health center."}],
    }),
    # DIY・ホーム
    ("diy-home-directory", "DIY Home Improvement Directory", "Curated directory of DIY home improvement resources and guides.", "Find DIY & Home Improvement Resources", {
        "DIY Guides": [{"title":"Family Handyman","url":"https://www.familyhandyman.com/","desc":"DIY home improvement projects and tips."}],
    }),
    ("gardening-directory", "Gardening Directory", "Curated directory of gardening resources, plant care, and landscaping.", "Find Gardening & Plant Care Resources", {
        "Plant Care": [{"title":"Gardeners.com","url":"https://www.gardeners.com/","desc":"Gardening supplies and plant care guides."}],
    }),
    # 料理
    ("cooking-directory", "Cooking & Recipes Directory", "Curated directory of cooking resources, recipes, and techniques.", "Find Cooking & Recipe Resources", {
        "Recipes": [{"title":"Allrecipes","url":"https://www.allrecipes.com/","desc":"Millions of recipes from home cooks."}],
    }),
    ("baking-directory", "Baking Directory", "Curated directory of baking resources, recipes, and techniques.", "Find Baking & Dessert Resources", {
        "Baking": [{"title":"King Arthur Baking","url":"https://www.kingarthurbaking.com/","desc":"Baking recipes and techniques."}],
    }),
    # 旅行
    ("travel-directory", "Travel Directory", "Curated directory of travel resources, destinations, and planning.", "Find Travel & Destination Resources", {
        "Destinations": [{"title":"Lonely Planet","url":"https://www.lonelyplanet.com/","desc":"Travel guides and destination information."}],
    }),
    ("camping-directory", "Camping & Outdoors Directory", "Curated directory of camping and outdoor recreation resources.", "Find Camping & Outdoor Resources", {
        "Camping": [{"title":"REI Expert Advice","url":"https://www.rei.com/learn","desc":"Camping and outdoor gear guides."}],
    }),
    # 健康・フィットネス
    ("fitness-directory", "Fitness Directory", "Curated directory of fitness resources, workouts, and health.", "Find Fitness & Workout Resources", {
        "Workouts": [{"title":"Bodybuilding.com","url":"https://www.bodybuilding.com/","desc":"Workout plans and fitness guides."}],
    }),
    ("yoga-directory", "Yoga Directory", "Curated directory of yoga resources, poses, and practice.", "Find Yoga & Meditation Resources", {
        "Yoga": [{"title":"Yoga Journal","url":"https://www.yogajournal.com/","desc":"Yoga poses, sequences, and practice guides."}],
    }),
    ("nutrition-directory", "Nutrition Directory", "Curated directory of nutrition resources and healthy eating.", "Find Nutrition & Healthy Eating Resources", {
        "Nutrition": [{"title":"EatRight","url":"https://www.eatright.org/","desc":"Academy of Nutrition and Dietetics."}],
    }),
    # 趣味
    ("photography-directory", "Photography Directory", "Curated directory of photography resources, techniques, and gear.", "Find Photography & Camera Resources", {
        "Photography": [{"title":"DPReview","url":"https://www.dpreview.com/","desc":"Camera reviews and photography guides."}],
    }),
    ("knitting-directory", "Knitting & Crochet Directory", "Curated directory of knitting and crochet resources.", "Find Knitting & Crochet Resources", {
        "Knitting": [{"title":"Ravelry","url":"https://www.ravelry.com/","desc":"Knitting and crochet patterns and community."}],
    }),
    ("woodworking-directory", "Woodworking Directory", "Curated directory of woodworking resources and projects.", "Find Woodworking & Craft Resources", {
        "Woodworking": [{"title":"Wood Magazine","url":"https://www.woodmagazine.com/","desc":"Woodworking projects and techniques."}],
    }),
    # 教育・子育て
    ("parenting-directory", "Parenting Directory", "Curated directory of parenting resources and child development.", "Find Parenting & Child Care Resources", {
        "Parenting": [{"title":"Parents.com","url":"https://www.parents.com/","desc":"Parenting advice and child development."}],
    }),
    ("homeschool-directory", "Homeschool Directory", "Curated directory of homeschooling resources and curriculum.", "Find Homeschool & Education Resources", {
        "Homeschool": [{"title":"Homeschool.com","url":"https://www.homeschool.com/","desc":"Homeschooling resources and curriculum."}],
    }),
    # テクノロジー
    ("tech-gadgets-directory", "Tech Gadgets Directory", "Curated directory of technology gadgets and reviews.", "Find Tech & Gadget Resources", {
        "Gadgets": [{"title":"The Verge","url":"https://www.theverge.com/","desc":"Technology news and gadget reviews."}],
    }),
    ("software-directory", "Software Directory", "Curated directory of software tools and applications.", "Find Software & App Resources", {
        "Software": [{"title":"AlternativeTo","url":"https://alternativeto.net/","desc":"Find software alternatives and tools."}],
    }),
    # 自動車
    ("car-care-directory", "Car Care Directory", "Curated directory of car maintenance and care resources.", "Find Car Care & Maintenance Resources", {
        "Car Care": [{"title":"Car and Driver","url":"https://www.caranddriver.com/","desc":"Car reviews and maintenance guides."}],
    }),
    # 環境・サステナビリティ
    ("sustainability-directory", "Sustainability Directory", "Curated directory of sustainability and eco-friendly resources.", "Find Sustainability & Eco Resources", {
        "Sustainability": [{"title":"Treehugger","url":"https://www.treehugger.com/","desc":"Sustainability and eco-friendly living."}],
    }),
    # ペット追加
    ("fish-keeping-directory", "Fish Keeping Directory", "Curated directory of aquarium and fish keeping resources.", "Find Aquarium & Fish Care Resources", {
        "Aquarium": [{"title":"Aquarium Co-Op","url":"https://www.aquariumcoop.com/","desc":"Aquarium and fish keeping guides."}],
    }),
    ("bird-care-directory", "Bird Care Directory", "Curated directory of pet bird care resources.", "Find Pet Bird Care Resources", {
        "Bird Care": [{"title":"Lafeber","url":"https://lafeber.com/","desc":"Pet bird care and nutrition."}],
    }),
    # ホーム追加
    ("interior-design-directory", "Interior Design Directory", "Curated directory of interior design resources and inspiration.", "Find Interior Design Resources", {
        "Design": [{"title":"Houzz","url":"https://www.houzz.com/","desc":"Interior design ideas and professionals."}],
    }),
    ("cleaning-directory", "Cleaning Directory", "Curated directory of home cleaning resources and tips.", "Find Home Cleaning Resources", {
        "Cleaning": [{"title":"Good Housekeeping","url":"https://www.goodhousekeeping.com/","desc":"Home cleaning tips and guides."}],
    }),
    ("laundry-directory", "Laundry Directory", "Curated directory of laundry care resources and tips.", "Find Laundry & Fabric Care Resources", {
        "Laundry": [{"title":"The Spruce","url":"https://www.thespruce.com/","desc":"Laundry and fabric care tips."}],
    }),
    # 料理追加
    ("grilling-directory", "Grilling & BBQ Directory", "Curated directory of grilling and BBQ resources.", "Find Grilling & BBQ Resources", {
        "Grilling": [{"title":"AmazingRibs","url":"https://amazingribs.com/","desc":"BBQ and grilling science and recipes."}],
    }),
    ("coffee-directory", "Coffee Directory", "Curated directory of coffee resources, brewing, and beans.", "Find Coffee & Brewing Resources", {
        "Coffee": [{"title":"Home-Barista","url":"https://www.home-barista.com/","desc":"Coffee brewing and espresso guides."}],
    }),
    ("wine-directory", "Wine Directory", "Curated directory of wine resources and tasting.", "Find Wine & Tasting Resources", {
        "Wine": [{"title":"Wine Spectator","url":"https://www.winespectator.com/","desc":"Wine reviews and tasting guides."}],
    }),
    # 旅行追加
    ("hiking-directory", "Hiking Directory", "Curated directory of hiking trails and outdoor resources.", "Find Hiking & Trail Resources", {
        "Hiking": [{"title":"AllTrails","url":"https://www.alltrails.com/","desc":"Hiking trails and outdoor guides."}],
    }),
    ("roadtrip-directory", "Road Trip Directory", "Curated directory of road trip planning resources.", "Find Road Trip & Travel Resources", {
        "Road Trip": [{"title":"Roadtrippers","url":"https://roadtrippers.com/","desc":"Road trip planning and routes."}],
    }),
    # 健康追加
    ("sleep-directory", "Sleep Directory", "Curated directory of sleep health resources.", "Find Sleep & Wellness Resources", {
        "Sleep": [{"title":"Sleep Foundation","url":"https://www.sleepfoundation.org/","desc":"Sleep health and improvement guides."}],
    }),
    ("mental-health-directory", "Mental Health Directory", "Curated directory of mental health resources and support.", "Find Mental Health & Support Resources", {
        "Mental Health": [{"title":"NAMI","url":"https://www.nami.org/","desc":"Mental health support and resources."}],
    }),
    ("meditation-directory", "Meditation Directory", "Curated directory of meditation and mindfulness resources.", "Find Meditation & Mindfulness Resources", {
        "Meditation": [{"title":"Headspace","url":"https://www.headspace.com/","desc":"Meditation and mindfulness guides."}],
    }),
    # 趣味追加
    ("painting-directory", "Painting Directory", "Curated directory of painting and art resources.", "Find Painting & Art Resources", {
        "Painting": [{"title":"Artists Network","url":"https://www.artistsnetwork.com/","desc":"Painting techniques and art guides."}],
    }),
    ("drawing-directory", "Drawing Directory", "Curated directory of drawing and illustration resources.", "Find Drawing & Illustration Resources", {
        "Drawing": [{"title":"Drawabox","url":"https://drawabox.com/","desc":"Drawing fundamentals and practice."}],
    }),
    ("pottery-directory", "Pottery Directory", "Curated directory of pottery and ceramics resources.", "Find Pottery & Ceramics Resources", {
        "Pottery": [{"title":"Ceramic Arts Network","url":"https://ceramicartsnetwork.org/","desc":"Pottery and ceramics techniques."}],
    }),
    ("sewing-directory", "Sewing Directory", "Curated directory of sewing and quilting resources.", "Find Sewing & Quilting Resources", {
        "Sewing": [{"title":"Sewing.com","url":"https://www.sewing.com/","desc":"Sewing patterns and techniques."}],
    }),
    ("embroidery-directory", "Embroidery Directory", "Curated directory of embroidery resources.", "Find Embroidery & Needlework Resources", {
        "Embroidery": [{"title":"Needle 'n Thread","url":"https://www.needlenthread.com/","desc":"Embroidery techniques and tutorials."}],
    }),
    # 教育追加
    ("language-learning-directory", "Language Learning Directory", "Curated directory of language learning resources.", "Find Language Learning Resources", {
        "Languages": [{"title":"Duolingo","url":"https://www.duolingo.com/","desc":"Language learning app and courses."}],
    }),
    ("coding-kids-directory", "Coding for Kids Directory", "Curated directory of coding resources for children.", "Find Kids Coding Resources", {
        "Kids Coding": [{"title":"Code.org","url":"https://code.org/","desc":"Coding education for kids."}],
    }),
    # テクノロジー追加
    ("cybersecurity-directory", "Cybersecurity Directory", "Curated directory of cybersecurity resources and tools.", "Find Cybersecurity Resources", {
        "Security": [{"title":"Krebs on Security","url":"https://krebsonsecurity.com/","desc":"Cybersecurity news and guides."}],
    }),
    ("ai-tools-directory", "AI Tools Directory", "Curated directory of AI tools and applications.", "Find AI Tools & Applications", {
        "AI Tools": [{"title":"Futurepedia","url":"https://www.futurepedia.io/","desc":"Directory of AI tools."}],
    }),
    # 自動車追加
    ("motorcycle-directory", "Motorcycle Directory", "Curated directory of motorcycle resources and maintenance.", "Find Motorcycle & Riding Resources", {
        "Motorcycle": [{"title":"Motorcycle.com","url":"https://www.motorcycle.com/","desc":"Motorcycle reviews and guides."}],
    }),
    ("rv-directory", "RV Directory", "Curated directory of RV and camping resources.", "Find RV & Camping Resources", {
        "RV": [{"title":"RV Life","url":"https://rvlife.com/","desc":"RV living and travel guides."}],
    }),
    # 環境追加
    ("recycling-directory", "Recycling Directory", "Curated directory of recycling and waste reduction resources.", "Find Recycling & Waste Resources", {
        "Recycling": [{"title":"Earth911","url":"https://earth911.com/","desc":"Recycling and waste reduction guides."}],
    }),
    ("composting-directory", "Composting Directory", "Curated directory of composting resources.", "Find Composting & Garden Resources", {
        "Composting": [{"title":"Compost Guide","url":"https://compostguide.com/","desc":"Composting methods and guides."}],
    }),
    # 音楽
    ("guitar-directory", "Guitar Directory", "Curated directory of guitar learning resources.", "Find Guitar & Music Resources", {
        "Guitar": [{"title":"Justin Guitar","url":"https://www.justinguitar.com/","desc":"Free guitar lessons."}],
    }),
    ("piano-directory", "Piano Directory", "Curated directory of piano learning resources.", "Find Piano & Keyboard Resources", {
        "Piano": [{"title":"Piano Marvel","url":"https://pianomarvel.com/","desc":"Piano learning software."}],
    }),
    # スポーツ
    ("running-directory", "Running Directory", "Curated directory of running and marathon resources.", "Find Running & Marathon Resources", {
        "Running": [{"title":"Runner's World","url":"https://www.runnersworld.com/","desc":"Running training and gear guides."}],
    }),
    ("cycling-directory", "Cycling Directory", "Curated directory of cycling resources.", "Find Cycling & Bike Resources", {
        "Cycling": [{"title":"Bicycling","url":"https://www.bicycling.com/","desc":"Cycling training and gear."}],
    }),
    ("swimming-directory", "Swimming Directory", "Curated directory of swimming resources.", "Find Swimming & Water Sports Resources", {
        "Swimming": [{"title":"Swim England","url":"https://www.swimming.org/","desc":"Swimming techniques and training."}],
    }),
    # ビジネス・キャリア（金融以外）
    ("freelancing-directory", "Freelancing Directory", "Curated directory of freelancing resources and platforms.", "Find Freelancing & Remote Work Resources", {
        "Freelancing": [{"title":"Upwork","url":"https://www.upwork.com/","desc":"Freelance work platform."}],
    }),
    ("resume-directory", "Resume Directory", "Curated directory of resume and job search resources.", "Find Resume & Job Search Resources", {
        "Resume": [{"title":"Resume.com","url":"https://www.resume.com/","desc":"Resume building and job search."}],
    }),
    ("interview-directory", "Interview Directory", "Curated directory of interview preparation resources.", "Find Interview & Career Resources", {
        "Interview": [{"title":"Glassdoor","url":"https://www.glassdoor.com/","desc":"Interview tips and company reviews."}],
    }),
    # 家庭
    ("wedding-directory", "Wedding Directory", "Curated directory of wedding planning resources.", "Find Wedding & Event Resources", {
        "Wedding": [{"title":"The Knot","url":"https://www.theknot.com/","desc":"Wedding planning resources."}],
    }),
    ("baby-directory", "Baby Directory", "Curated directory of baby care resources.", "Find Baby & Newborn Care Resources", {
        "Baby": [{"title":"What to Expect","url":"https://www.whattoexpect.com/","desc":"Pregnancy and baby care guides."}],
    }),
    # ペット追加2
    ("reptile-directory", "Reptile Directory", "Curated directory of reptile care resources.", "Find Reptile & Exotic Pet Resources", {
        "Reptile": [{"title":"Reptiles Magazine","url":"https://www.reptilesmagazine.com/","desc":"Reptile care and husbandry."}],
    }),
    ("horse-directory", "Horse Directory", "Curated directory of horse care and riding resources.", "Find Horse & Equestrian Resources", {
        "Horse": [{"title":"The Horse","url":"https://thehorse.com/","desc":"Horse health and care."}],
    }),
    # ホーム追加2
    ("furniture-directory", "Furniture Directory", "Curated directory of furniture and home decor resources.", "Find Furniture & Decor Resources", {
        "Furniture": [{"title":"Wayfair","url":"https://www.wayfair.com/","desc":"Furniture and home decor."}],
    }),
    ("appliance-directory", "Appliance Directory", "Curated directory of home appliance resources.", "Find Appliance & Repair Resources", {
        "Appliance": [{"title":"Repair Clinic","url":"https://www.repairclinic.com/","desc":"Appliance repair guides."}],
    }),
    # 料理追加2
    ("vegan-directory", "Vegan Directory", "Curated directory of vegan and plant-based resources.", "Find Vegan & Plant-Based Resources", {
        "Vegan": [{"title":"Forks Over Knives","url":"https://www.forksoverknives.com/","desc":"Plant-based recipes and guides."}],
    }),
    ("glutenfree-directory", "Gluten-Free Directory", "Curated directory of gluten-free resources.", "Find Gluten-Free & Allergy Resources", {
        "Gluten-Free": [{"title":"Gluten-Free Living","url":"https://glutenfreeliving.com/","desc":"Gluten-free recipes and guides."}],
    }),
    # 旅行追加2
    ("beach-directory", "Beach Directory", "Curated directory of beach and coastal travel resources.", "Find Beach & Coastal Resources", {
        "Beach": [{"title":"Beach.com","url":"https://www.beach.com/","desc":"Beach destinations and guides."}],
    }),
    ("ski-directory", "Ski Directory", "Curated directory of skiing and snowboarding resources.", "Find Ski & Snowboard Resources", {
        "Ski": [{"title":"Ski Magazine","url":"https://www.skimag.com/","desc":"Skiing destinations and gear."}],
    }),
    # 健康追加2
    ("dental-directory", "Dental Directory", "Curated directory of dental health resources.", "Find Dental & Oral Health Resources", {
        "Dental": [{"title":"Colgate","url":"https://www.colgate.com/","desc":"Dental health and oral care."}],
    }),
    ("vision-directory", "Vision Directory", "Curated directory of eye health resources.", "Find Vision & Eye Health Resources", {
        "Vision": [{"title":"All About Vision","url":"https://www.allaboutvision.com/","desc":"Eye health and vision care."}],
    }),
    # 趣味追加2
    ("origami-directory", "Origami Directory", "Curated directory of origami and paper craft resources.", "Find Origami & Paper Craft Resources", {
        "Origami": [{"title":"Origami.me","url":"https://origami.me/","desc":"Origami instructions and diagrams."}],
    }),
    ("model-building-directory", "Model Building Directory", "Curated directory of model building resources.", "Find Model & Hobby Resources", {
        "Models": [{"title":"FineScale Modeler","url":"https://finescale.com/","desc":"Model building techniques."}],
    }),
    # 教育追加2
    ("college-prep-directory", "College Prep Directory", "Curated directory of college preparation resources.", "Find College Prep & Admission Resources", {
        "College": [{"title":"College Board","url":"https://www.collegeboard.org/","desc":"College admission and SAT resources."}],
    }),
    ("study-skills-directory", "Study Skills Directory", "Curated directory of study skills and learning resources.", "Find Study & Learning Resources", {
        "Study": [{"title":"Khan Academy","url":"https://www.khanacademy.org/","desc":"Free study and learning resources."}],
    }),
    # テクノロジー追加2
    ("webdev-directory", "Web Development Directory", "Curated directory of web development resources.", "Find Web Dev & Coding Resources", {
        "Web Dev": [{"title":"MDN Web Docs","url":"https://developer.mozilla.org/","desc":"Web development documentation."}],
    }),
    ("datascience-directory", "Data Science Directory", "Curated directory of data science resources.", "Find Data Science & ML Resources", {
        "Data Science": [{"title":"Kaggle","url":"https://www.kaggle.com/","desc":"Data science competitions and datasets."}],
    }),
    # 自動車追加2
    ("boat-directory", "Boating Directory", "Curated directory of boating and marine resources.", "Find Boating & Marine Resources", {
        "Boating": [{"title":"BoatUS","url":"https://www.boatus.com/","desc":"Boating safety and resources."}],
    }),
    ("bicycle-directory", "Bicycle Directory", "Curated directory of bicycle resources.", "Find Bicycle & Commuting Resources", {
        "Bicycle": [{"title":"BikeRadar","url":"https://www.bikeradar.com/","desc":"Bicycle reviews and guides."}],
    }),
    # 環境追加2
    ("solar-directory", "Solar Directory", "Curated directory of solar energy resources.", "Find Solar & Renewable Energy Resources", {
        "Solar": [{"title":"EnergySage","url":"https://www.energysage.com/","desc":"Solar energy comparison and guides."}],
    }),
    ("water-conservation-directory", "Water Conservation Directory", "Curated directory of water conservation resources.", "Find Water Conservation Resources", {
        "Water": [{"title":"Water Use It Wisely","url":"https://wateruseitwisely.com/","desc":"Water conservation tips."}],
    }),
    # 音楽追加
    ("drums-directory", "Drums Directory", "Curated directory of drum learning resources.", "Find Drums & Percussion Resources", {
        "Drums": [{"title":"Drumeo","url":"https://www.drumeo.com/","desc":"Drum lessons and techniques."}],
    }),
    ("singing-directory", "Singing Directory", "Curated directory of singing and vocal resources.", "Find Singing & Vocal Resources", {
        "Singing": [{"title":"Singwise","url":"https://singwise.com/","desc":"Vocal technique and singing guides."}],
    }),
    # スポーツ追加
    ("tennis-directory", "Tennis Directory", "Curated directory of tennis resources.", "Find Tennis & Racquet Resources", {
        "Tennis": [{"title":"Tennis.com","url":"https://www.tennis.com/","desc":"Tennis news and technique."}],
    }),
    ("golf-directory", "Golf Directory", "Curated directory of golf resources.", "Find Golf & Course Resources", {
        "Golf": [{"title":"Golf Digest","url":"https://www.golfdigest.com/","desc":"Golf tips and equipment."}],
    }),
    # ビジネス追加
    ("marketing-directory", "Marketing Directory", "Curated directory of marketing resources.", "Find Marketing & Growth Resources", {
        "Marketing": [{"title":"HubSpot Blog","url":"https://blog.hubspot.com/","desc":"Marketing guides and resources."}],
    }),
    ("ecommerce-directory", "Ecommerce Directory", "Curated directory of ecommerce resources.", "Find Ecommerce & Online Store Resources", {
        "Ecommerce": [{"title":"Shopify Blog","url":"https://www.shopify.com/blog","desc":"Ecommerce guides and resources."}],
    }),
    # 家庭追加
    ("moving-directory", "Moving Directory", "Curated directory of moving and relocation resources.", "Find Moving & Relocation Resources", {
        "Moving": [{"title":"Moving.com","url":"https://www.moving.com/","desc":"Moving and relocation guides."}],
    }),
    ("storage-directory", "Storage Directory", "Curated directory of storage and organization resources.", "Find Storage & Organization Resources", {
        "Storage": [{"title":"The Container Store","url":"https://www.containerstore.com/","desc":"Storage and organization solutions."}],
    }),
    # ペット追加3
    ("hamster-directory", "Small Pet Directory", "Curated directory of small pet care resources.", "Find Small Pet & Rodent Resources", {
        "Small Pets": [{"title":"Small Pet Select","url":"https://smallpetselect.com/","desc":"Small pet care and nutrition."}],
    }),
    # ホーム追加3
    ("pest-control-directory", "Pest Control Directory", "Curated directory of pest control resources.", "Find Pest Control & Prevention Resources", {
        "Pest Control": [{"title":"PestWorld","url":"https://www.pestworld.org/","desc":"Pest control and prevention guides."}],
    }),
    # 料理追加3
    ("sourdough-directory", "Sourdough Directory", "Curated directory of sourdough baking resources.", "Find Sourdough & Bread Resources", {
        "Sourdough": [{"title":"The Perfect Loaf","url":"https://www.theperfectloaf.com/","desc":"Sourdough baking guides."}],
    }),
    # 旅行追加3
    ("cruise-directory", "Cruise Directory", "Curated directory of cruise travel resources.", "Find Cruise & Sea Travel Resources", {
        "Cruise": [{"title":"Cruise Critic","url":"https://www.cruisecritic.com/","desc":"Cruise reviews and guides."}],
    }),
    # 健康追加3
    ("posture-directory", "Posture Directory", "Curated directory of posture and ergonomics resources.", "Find Posture & Ergonomics Resources", {
        "Posture": [{"title":"Posture Direct","url":"https://posturedirect.com/","desc":"Posture correction guides."}],
    }),
    # 趣味追加3
    ("calligraphy-directory", "Calligraphy Directory", "Curated directory of calligraphy resources.", "Find Calligraphy & Lettering Resources", {
        "Calligraphy": [{"title":"The Postman's Knock","url":"https://thepostmansknock.com/","desc":"Calligraphy tutorials and guides."}],
    }),
    # 教育追加3
    ("tutoring-directory", "Tutoring Directory", "Curated directory of tutoring resources.", "Find Tutoring & Academic Help Resources", {
        "Tutoring": [{"title":"Tutor.com","url":"https://www.tutor.com/","desc":"Online tutoring services."}],
    }),
    # テクノロジー追加3
    ("smart-home-directory", "Smart Home Directory", "Curated directory of smart home resources.", "Find Smart Home & IoT Resources", {
        "Smart Home": [{"title":"Smart Home Solver","url":"https://smarthomesolver.com/","desc":"Smart home guides and reviews."}],
    }),
    # 自動車追加3
    ("tire-directory", "Tire Directory", "Curated directory of tire resources.", "Find Tire & Wheel Resources", {
        "Tires": [{"title":"Tire Rack","url":"https://www.tirerack.com/","desc":"Tire reviews and guides."}],
    }),
    # 環境追加3
    ("beekeeping-directory", "Beekeeping Directory", "Curated directory of beekeeping resources.", "Find Beekeeping & Apiary Resources", {
        "Beekeeping": [{"title":"Bee Culture","url":"https://www.beeculture.com/","desc":"Beekeeping guides and resources."}],
    }),
    # 音楽追加3
    ("ukulele-directory", "Ukulele Directory", "Curated directory of ukulele learning resources.", "Find Ukulele & String Resources", {
        "Ukulele": [{"title":"Ukulele Underground","url":"https://ukuleleunderground.com/","desc":"Ukulele lessons and community."}],
    }),
    # スポーツ追加3
    ("basketball-directory", "Basketball Directory", "Curated directory of basketball resources.", "Find Basketball & Training Resources", {
        "Basketball": [{"title":"Basketball For Coaches","url":"https://www.basketballforcoaches.com/","desc":"Basketball drills and coaching."}],
    }),
    # ビジネス追加3
    ("productivity-directory", "Productivity Directory", "Curated directory of productivity resources.", "Find Productivity & Time Management Resources", {
        "Productivity": [{"title":"Todoist Blog","url":"https://todoist.com/productivity-methods","desc":"Productivity methods and tools."}],
    }),
    # 家庭追加3
    ("decluttering-directory", "Decluttering Directory", "Curated directory of decluttering resources.", "Find Decluttering & Minimalism Resources", {
        "Decluttering": [{"title":"The Minimalists","url":"https://www.theminimalists.com/","desc":"Decluttering and minimalism guides."}],
    }),
]

def main():
    ok = 0
    fail = 0
    for slug, name, desc, kicker, cats in NICHES:
        site = {
            "name": name,
            "slug": slug,
            "domain": f"{slug}.pages.dev",
            "description": desc,
            "kicker": kicker,
        }
        try:
            build_directory(site, cats)
            ok += 1
            print(f"✅ {slug}")
        except Exception as e:
            fail += 1
            print(f"❌ {slug}: {e}")
    print(f"\n=== 生成完了: {ok}/{len(NICHES)} 成功, {fail} 失敗 ===")

if __name__ == "__main__":
    main()
