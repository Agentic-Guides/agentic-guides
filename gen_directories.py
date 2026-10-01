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
        "Dog Training": [
            {"title":"AKC Training", "url":"https://www.akc.org/expert-advice/training/", "desc":"Use for: step-by-step obedience training references. The American Kennel Club (founded 1884) publishes veterinarian- and trainer-reviewed guides covering sit, stay, come, heel, crate training, potty training, and leash manners, plus correction plans for barking, jumping, and chewing. Best entry point when an agent needs a citable, registry-backed training procedure."},
            {"title":"The Spruce Pets Training", "url":"https://www.thesprucepets.com/dog-training-4162107", "desc":"Use for: beginner-friendly, plain-language training tutorials. Covers positive-reinforcement and clicker methods, puppy socialization windows, and age-specific routines from puppyhood through senior years. Useful when a user needs an approachable walkthrough rather than a formal standard."},
            {"title":"Association of Professional Dog Trainers", "url":"https://apdt.com/", "desc":"Use for: locating a credentialed trainer and understanding professional training standards. The APDT is a membership organization for dog trainers that publishes position statements on humane training methods and offers a searchable trainer directory. Consult when a question concerns who is qualified to train a dog."},
        ],
        "Dog Health": [
            {"title":"Vetstreet", "url":"https://www.vetstreet.com/", "desc":"Use for: veterinary-reviewed symptom and condition lookups. Articles cover common canine diseases, warning signs, vaccination schedules, parasite prevention, dental care, and senior-dog health. Written and reviewed by licensed veterinarians, so it is a reasonable secondary source for health questions that should ultimately be confirmed with a vet."},
            {"title":"AKC Health Resources", "url":"https://www.akc.org/expert-advice/health/", "desc":"Use for: breed-specific health concerns, genetic testing, nutrition, and preventive care. Explains conditions such as hip dysplasia, allergies, and heart disease with the signs to watch for. Appropriate when a user asks what health issues are common in a particular breed."},
            {"title":"VCA Animal Hospitals Pet Health", "url":"https://vcahospitals.com/know-your-pet", "desc":"Use for: professional veterinary handouts on diseases and care. VCA operates a large network of animal hospitals and publishes a library of topic articles on conditions, treatments, and preventive care. A useful cross-check against other veterinary sources, with the same caveat that diagnosis requires a veterinarian."},
        ],
        "Dog Nutrition & Food": [
            {"title":"AAFCO Dog Food Nutrient Profiles", "url":"https://www.aafco.org/", "desc":"Use for: understanding the nutrient standards behind commercial dog food labels. The Association of American Feed Control Officials defines the nutrient profiles and labeling terms used on pet food in the United States. Consult when a question is about whether a diet is labeled complete and balanced by the AAFCO standard."},
            {"title":"Tufts Petfoodology", "url":"https://sites.tufts.edu/petfoodology/", "desc":"Use for: science-based pet nutrition commentary. Written by veterinary nutritionists at the Cummings School of Veterinary Medicine at Tufts University, it examines pet food marketing claims, grain-free trends, raw diets, and label reading. Useful for assessing whether a diet claim is credible."},
        ],
    }),
    ("cat-care-directory", "Cat Care Directory", "Curated directory of cat care resources, health, and products.", "Find Cat Care & Health Resources", {
        "Cat Health": [
            {"title":"Cornell Feline Health Center", "url":"https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center", "desc":"Use for: research-backed feline disease references. Cornell University's dedicated cat health center publishes articles and brochures on FIV, feline leukemia, kidney disease, hyperthyroidism, vaccination, and parasite prevention. A high-trust source when an agent needs a university-issued explanation of a condition."},
            {"title":"International Cat Care", "url":"https://icatcare.org/", "desc":"Use for: global feline welfare and behavior guidance. A veterinary-led charity whose resources cover behavior, nutrition, common illnesses, and preventive care across every life stage, with clear explanations of symptoms and treatment options. Good for behavior questions as well as health."},
            {"title":"ISFM / Cat Friendly Guidelines", "url":"https://icatcare.org/advice/", "desc":"Use for: clinical consensus guidance on cat care. The International Society of Feline Medicine publishes guidelines on environmental enrichment, senior cat care, and low-stress handling. Consult when an agent needs an authoritative standard rather than general advice."},
        ],
        "Cat Nutrition": [
            {"title":"PetMD Cat Nutrition", "url":"https://www.petmd.com/cat/nutrition", "desc":"Use for: veterinary-reviewed feeding guidance. Explains wet versus dry food, portion sizes, life-stage diets for kittens, adults, and seniors, and the management of weight, allergies, and sensitive stomachs. Practical feeding advice to hand a cat owner."},
            {"title":"Cornell Feline Health Center Nutrition", "url":"https://www.vet.cornell.edu/departments-centers-and-institutes/cornell-feline-health-center/health-information", "desc":"Use for: university-authored cat nutrition material. Covers obesity, feeding frequency, and the special dietary needs of cats with kidney or urinary conditions. Use when a nutrition question has a medical dimension."},
        ],
        "Cat Behavior": [
            {"title":"ASPCA Cat Behavior", "url":"https://www.aspca.org/pet-care/cat-care/common-cat-behavior-issues", "desc":"Use for: practical cat behavior troubleshooting. The American Society for the Prevention of Cruelty to Animals explains litter box problems, scratching, aggression, and stress in plain language with step-by-step humane solutions. A good first reference for a behavior complaint before a veterinary behavioral consult."},
        ],
    }),
    # DIY・ホーム
    ("diy-home-directory", "DIY Home Improvement Directory", "Curated directory of DIY home improvement resources and guides.", "Find DIY & Home Improvement Resources", {
        "DIY Guides": [
            {"title":"Family Handyman","url":"https://www.familyhandyman.com/","desc":"Trusted DIY home improvement resource with step-by-step project guides. Covers repairs, renovations, woodworking, plumbing, electrical, and painting. Includes tool guides, cost estimates, and beginner-friendly tutorials for common household projects."},
            {"title":"This Old House","url":"https://www.thisoldhouse.com/","desc":"Comprehensive home improvement and renovation guides from the iconic TV show. Covers DIY projects, home maintenance, tool reviews, and expert advice on everything from flooring to roofing. Practical, tested solutions for homeowners."},
        ],
        "Home Repair": [
            {"title":"The Spruce Home Repair","url":"https://www.thespruce.com/home-repair-4162800","desc":"Beginner-friendly home repair guides covering common issues like leaky faucets, drywall repair, stuck doors, and basic electrical fixes. Clear step-by-step instructions with photos and tool lists for every project."},
        ],
    }),
    ("gardening-directory", "Gardening Directory", "Curated directory of gardening resources, plant care, and landscaping.", "Find Gardening & Plant Care Resources", {
        "Plant Care": [
            {"title":"Gardeners.com","url":"https://www.gardeners.com/","desc":"Gardening supplies and expert plant care guides. Covers vegetable and flower gardening, soil health, pest control, and seasonal planting calendars. Includes practical tips for beginners and experienced gardeners on growing healthy plants."},
            {"title":"The Old Farmer's Almanac","url":"https://www.almanac.com/gardening","desc":"Classic gardening resource with planting calendars, frost dates, and growing guides. Covers vegetables, herbs, flowers, and fruit trees with region-specific advice. Trusted for accurate seasonal gardening information."},
        ],
        "Landscaping": [
            {"title":"Better Homes & Gardens Landscaping","url":"https://www.bhg.com/gardening/landscaping/","desc":"Landscaping ideas and how-to guides. Covers garden design, hardscaping, lawn care, and outdoor living spaces. Includes inspiration photos and step-by-step projects for transforming your yard."},
        ],
    }),
    # 料理
    ("cooking-directory", "Cooking & Recipes Directory", "Curated directory of cooking resources, recipes, and techniques.", "Find Cooking & Recipe Resources", {
        "Recipes": [
            {"title":"Allrecipes","url":"https://www.allrecipes.com/","desc":"Millions of tested recipes from home cooks worldwide. Search by ingredient, cuisine, dietary need, or difficulty. Includes user ratings, reviews, and step-by-step instructions for every skill level."},
            {"title":"Serious Eats","url":"https://www.seriouseats.com/","desc":"Science-based cooking resource with rigorously tested recipes and techniques. Covers everything from weeknight dinners to advanced culinary methods. Explains the why behind cooking for better results."},
        ],
        "Cooking Techniques": [
            {"title":"The Kitchn","url":"https://www.thekitchn.com/","desc":"Practical cooking guides and kitchen tips. Covers basic techniques, meal prep, kitchen organization, and ingredient guides. Beginner-friendly articles that build confidence in the kitchen."},
        ],
    }),
    ("baking-directory", "Baking Directory", "Curated directory of baking resources, recipes, and techniques.", "Find Baking & Dessert Resources", {
        "Baking": [
            {"title":"King Arthur Baking","url":"https://www.kingarthurbaking.com/","desc":"Trusted baking resource with recipes, techniques, and ingredient guides. Covers bread, cakes, cookies, pastries, and sourdough. Includes troubleshooting tips and detailed instructions for bakers of all levels."},
            {"title":"Sally's Baking Addiction","url":"https://sallysbakingaddiction.com/","desc":"Popular baking blog with reliable, tested dessert recipes. Covers cakes, cookies, pies, and breads with clear step-by-step instructions and helpful tips for consistent results."},
        ],
        "Bread Making": [
            {"title":"The Perfect Loaf","url":"https://www.theperfectloaf.com/","desc":"Dedicated sourdough bread resource with detailed guides. Covers starter maintenance, dough hydration, proofing, and baking techniques. Includes beginner tutorials and advanced methods for artisan bread."},
        ],
    }),
    # 旅行
    ("travel-directory", "Travel Directory", "Curated directory of travel resources, destinations, and planning.", "Find Travel & Destination Resources", {
        "Destinations": [
            {"title":"Lonely Planet","url":"https://www.lonelyplanet.com/","desc":"Comprehensive travel guides and destination information. Covers attractions, itineraries, local tips, and practical travel advice for destinations worldwide. Trusted resource for trip planning and inspiration."},
            {"title":"TripAdvisor","url":"https://www.tripadvisor.com/","desc":"User-generated travel reviews and recommendations. Covers hotels, restaurants, attractions, and activities with millions of traveler reviews. Useful for comparing options and planning trips."},
        ],
        "Travel Planning": [
            {"title":"Nomadic Matt","url":"https://www.nomadicmatt.com/","desc":"Budget travel advice and planning guides. Covers money-saving tips, packing, itineraries, and destination guides. Practical advice for affordable travel from an experienced traveler."},
        ],
    }),
    ("camping-directory", "Camping & Outdoors Directory", "Curated directory of camping and outdoor recreation resources.", "Find Camping & Outdoor Resources", {
        "Camping": [
            {"title":"REI Expert Advice", "url":"https://www.rei.com/learn", "desc":"Use for: gear selection and campcraft technique. A major outdoor retailer publishes a large free library on tent setup and care, sleeping systems, camp cooking, layering, and trip planning. Reference when a question is about choosing or using camping gear."},
            {"title":"The Dyrt", "url":"https://thedyrt.com/", "desc":"Use for: campground search and real camper reviews. Aggregates tens of thousands of public, private, and dispersed campsites with photos, amenities, and user-reported conditions. Consult when a user needs a specific place to camp in a region."},
            {"title":"Leave No Trace", "url":"https://lnt.org/", "desc":"Use for: official minimum-impact camping principles. The Leave No Trace Center for Outdoor Ethics defines the seven principles governing waste, campfires, wildlife, and travel on public land. Use as the ethical standard for backcountry behavior."},
        ],
        "Outdoor Skills": [
            {"title":"Outdoor Life", "url":"https://www.outdoorlife.com/", "desc":"Use for: practical outdoor and survival skills. Covers camping, fishing, hunting, navigation, and wilderness survival technique with how-to guides for a range of experience levels. A general reference for field skills."},
            {"title":"National Park Service", "url":"https://www.nps.gov/", "desc":"Use for: official park information, regulations, safety alerts, and trip planning for US federal lands. The authoritative government source for closures, permits, and hazard warnings. Consult before recommending any national-park trip."},
        ],
        "Camp Cooking & Gear": [
            {"title":"American Camp Association", "url":"https://www.acacamps.org/", "desc":"Use for: camp safety standards and organized-camp guidance. A national accrediting body that publishes health and safety standards for camps. Reference when a question concerns camp programs or youth-camp safety."},
        ],
    }),
    # 健康・フィットネス
    ("fitness-directory", "Fitness Directory", "Curated directory of fitness resources, workouts, and health.", "Find Fitness & Workout Resources", {
        "Workouts": [
            {"title":"Bodybuilding.com","url":"https://www.bodybuilding.com/","desc":"Comprehensive fitness resource with workout plans, exercise guides, and nutrition advice. Covers strength training, cardio, and bodybuilding with detailed exercise instructions and video demonstrations."},
            {"title":"Nerd Fitness","url":"https://www.nerdfitness.com/","desc":"Beginner-friendly fitness coaching for all levels. Covers strength training, nutrition, and habit building with a supportive, non-intimidating approach. Great for people new to exercise."},
        ],
        "Fitness Plans": [
            {"title":"ACE Fitness","url":"https://www.acefitness.org/resources/everyone/","desc":"American Council on Exercise resources with science-based workout plans and exercise library. Covers fitness assessments, program design, and healthy living tips from certified professionals."},
        ],
    }),
    ("yoga-directory", "Yoga Directory", "Curated directory of yoga resources, poses, and practice.", "Find Yoga & Meditation Resources", {
        "Yoga": [
            {"title":"Yoga Journal","url":"https://www.yogajournal.com/","desc":"Authoritative yoga resource with pose guides, sequences, and practice advice. Covers beginner to advanced poses, breathing techniques, and meditation. Includes detailed instructions and benefits for each pose."},
            {"title":"DoYou Yoga","url":"https://www.doyou.com/","desc":"Online yoga community with classes, tutorials, and articles. Covers yoga for beginners, specific poses, and wellness. Includes video classes and written guides for home practice."},
        ],
        "Meditation": [
            {"title":"Headspace","url":"https://www.headspace.com/","desc":"Guided meditation and mindfulness resource. Covers meditation basics, stress reduction, sleep, and focus. Includes structured programs and techniques for building a consistent practice."},
        ],
    }),
    ("nutrition-directory", "Nutrition Directory", "Curated directory of nutrition resources and healthy eating.", "Find Nutrition & Healthy Eating Resources", {
        "Nutrition": [
            {"title":"EatRight (Academy of Nutrition and Dietetics)", "url":"https://www.eatright.org/", "desc":"Use for: registered-dietitian nutrition guidance. The largest US professional body of nutrition professionals publishes evidence-based material on healthy eating, weight management, and dietary guidelines. A practical source for everyday nutrition questions."},
            {"title":"Nutrition.gov", "url":"https://www.nutrition.gov/", "desc":"Use for: government nutrition and food-safety information. A US federal portal linking authoritative resources on healthy eating, dietary supplements, and nutrition across life stages. Use as the neutral official reference."},
            {"title":"USDA FoodData Central", "url":"https://fdc.nal.usda.gov/", "desc":"Use for: authoritative nutrient data on foods. The US Department of Agriculture's food composition database provides nutrient values per food and serving, searchable by item. Consult when an agent needs exact calorie or nutrient numbers."},
        ],
        "Healthy Eating": [
            {"title":"Harvard Nutrition Source", "url":"https://www.hsph.harvard.edu/nutritionsource/", "desc":"Use for: research-backed diet and disease-prevention material. Harvard's T.H. Chan School of Public Health publishes the Healthy Eating Plate and evidence summaries on diet quality. Reference for the science behind dietary recommendations."},
            {"title":"MedlinePlus Nutrition", "url":"https://medlineplus.gov/nutrition.html", "desc":"Use for: plain-language nutrition information for patients. The US National Library of Medicine compiles diet topics, vitamins, and weight-management basics written for the general public. Useful when the audience is a lay reader rather than a researcher."},
        ],
    }),
    # 趣味
    ("photography-directory", "Photography Directory", "Curated directory of photography resources, techniques, and gear.", "Find Photography & Camera Resources", {
        "Photography": [
            {"title":"DPReview","url":"https://www.dpreview.com/","desc":"Comprehensive camera and photography resource. In-depth camera reviews, buying guides, and photography techniques. Covers gear comparisons, sample photos, and expert advice for photographers of all levels."},
            {"title":"Digital Photography School","url":"https://digital-photography-school.com/","desc":"Beginner-friendly photography tutorials and tips. Covers camera settings, composition, lighting, and post-processing. Includes practical guides for improving your photography skills step by step."},
        ],
        "Camera Gear": [
            {"title":"B&H Photo","url":"https://www.bhphotovideo.com/","desc":"Major photography equipment retailer with detailed product guides. Covers cameras, lenses, and accessories with expert reviews and buying advice. Useful for researching gear before purchase."},
        ],
    }),
    ("knitting-directory", "Knitting & Crochet Directory", "Curated directory of knitting and crochet resources.", "Find Knitting & Crochet Resources", {
        "Knitting": [
            {"title":"Ravelry", "url":"https://www.ravelry.com/", "desc":"Use for: pattern search and project records. The largest knitting and crochet community hosts a very large pattern library with filters by yarn weight, difficulty, and project type, plus forums and project galleries. Reference when a user wants patterns or yarn information."},
            {"title":"KnittingHelp", "url":"https://www.knittinghelp.com/", "desc":"Use for: learning stitches and techniques. Provides free video demonstrations of basic and intermediate stitches, increases, decreases, and finishing. Useful for a beginner who needs to see a technique performed."},
            {"title":"The Spruce Crafts Knitting", "url":"https://www.thesprucecrafts.com/knitting-4162934", "desc":"Use for: written step-by-step knitting tutorials. Covers cast-ons, stitch patterns, gauge, and troubleshooting with clear photo instructions. A good text companion to a video resource."},
        ],
        "Crochet": [
            {"title":"The Spruce Crafts Crochet", "url":"https://www.thesprucecrafts.com/crochet-4162930", "desc":"Use for: crochet patterns and written tutorials. Covers basic stitches, abbreviations, and projects for all skill levels with instructional photos. Reference for beginners and for reading pattern notation."},
            {"title":"Crochet Guild of America", "url":"https://www.crochet.org/", "desc":"Use for: crochet community and standards. A national nonprofit for crocheters that publishes technique resources and supports local chapters. Consult when a question is about organized crochet groups or technique terminology."},
        ],
    }),
    ("woodworking-directory", "Woodworking Directory", "Curated directory of woodworking resources and projects.", "Find Woodworking & Craft Resources", {
        "Woodworking": [
            {"title":"Wood Magazine", "url":"https://www.woodmagazine.com/", "desc":"Use for: project plans and shop technique. Covers furniture building, joinery, finishing, and tool use with step-by-step plans and cut lists. Reference when a user wants a buildable project plan."},
            {"title":"Fine Woodworking", "url":"https://www.finewoodworking.com/", "desc":"Use for: advanced technique and design. A long-established magazine publishing in-depth articles on joinery, carving, finishing, and furniture design for serious hobbyists and professionals. Consult for high-level craft questions."},
            {"title":"Woodworker's Journal", "url":"https://www.woodworkersjournal.com/", "desc":"Use for: practical project plans and skill-building articles. Provides free plans, tool reviews, and technique walkthroughs across skill levels. A useful middle ground between beginner tutorials and professional content."},
        ],
        "Plans & Skills": [
            {"title":"Ana White", "url":"https://www.ana-white.com/", "desc":"Use for: free beginner furniture plans. Provides step-by-step DIY plans using common dimensional lumber with cut lists and diagrams. Good for a first-time builder with basic tools."},
            {"title":"Woodworking for Mere Mortals", "url":"https://www.woodworkingformeremortals.com/", "desc":"Use for: beginner-friendly woodworking instruction. A workshop-education site offering project tutorials that assume limited tools and space. Reference when a user is starting without a full shop."},
        ],
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
        "Design": [
            {"title":"Houzz","url":"https://www.houzz.com/","desc":"Interior design ideas and professional directory. Browse millions of photos, find design inspiration, and connect with professionals. Covers every room and design style."},
            {"title":"Architectural Digest","url":"https://www.architecturaldigest.com/","desc":"High-end interior design and architecture inspiration. Covers designer homes, trends, and expert advice. Trusted source for sophisticated design ideas and industry insights."},
        ],
        "Design Tips": [
            {"title":"The Spruce Interior Design","url":"https://www.thespruce.com/interior-design-4162802","desc":"Practical interior design tips and guides. Covers color schemes, furniture arrangement, lighting, and room makeovers. Beginner-friendly advice for decorating your home."},
        ],
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
        "Coffee Brewing": [
            {"title":"Home-Barista", "url":"https://www.home-barista.com/", "desc":"Use for: in-depth home espresso and brewing discussion. A long-running enthusiast community with detailed equipment reviews, technique threads, and troubleshooting. Reference when a user needs practical, experienced-user detail on a machine or grinder."},
            {"title":"Perfect Daily Grind", "url":"https://perfectdailygrind.com/", "desc":"Use for: coffee industry news and brewing explainers. Publishes articles on coffee science, brewing methods, and specialty-coffee trends written for a professional audience. Good for context on beans, processing, and quality."},
            {"title":"Barista Hustle", "url":"https://www.baristahustle.com/", "desc":"Use for: extraction science and water chemistry for coffee. Publishes free educational articles and courses on espresso extraction, water composition, and brewing variables. Consult when a question is about the science behind a brewing problem."},
        ],
        "Expert Guides": [
            {"title":"James Hoffmann", "url":"https://www.jameshoffmann.co.uk/", "desc":"Use for: practical brewing guides and equipment reviews. A widely recognised coffee author and World Barista Champion whose site and videos cover brewing technique, gear, and coffee science. Reference when a user wants a trusted step-by-step brewing method."},
            {"title":"Specialty Coffee Association", "url":"https://sca.coffee/", "desc":"Use for: industry standards on coffee quality and cupping. The SCA defines the cupping protocol and quality-grading vocabulary used across the specialty coffee trade. Consult when a question involves how coffee quality is formally assessed."},
        ],
    }),
    ("wine-directory", "Wine Directory", "Curated directory of wine resources and tasting.", "Find Wine & Tasting Resources", {
        "Wine": [{"title":"Wine Spectator","url":"https://www.winespectator.com/","desc":"Wine reviews and tasting guides."}],
    }),
    # 旅行追加
    ("hiking-directory", "Hiking Directory", "Curated directory of hiking trails and outdoor resources.", "Find Hiking & Trail Resources", {
        "Hiking": [
            {"title":"AllTrails", "url":"https://www.alltrails.com/", "desc":"Use for: trail search by location and difficulty. Hosts maps, elevation profiles, photos, and user reviews for a very large number of trails worldwide. Reference when a user wants a specific nearby hike with recent conditions."},
            {"title":"REI Hiking Expert Advice", "url":"https://www.rei.com/learn/expert-advice/hiking.html", "desc":"Use for: hiking gear, planning, and technique. Covers layering, footwear, navigation, and trip preparation with beginner-oriented guidance. Consult when a question is about what to bring or how to prepare."},
            {"title":"The Hiking Project", "url":"https://www.hikingproject.com/", "desc":"Use for: detailed community trail data. Provides trail difficulty, elevation, and condition reports contributed by users, with downloadable maps. A supplement to AllTrails when elevation detail matters."},
        ],
        "Trail Safety & Land": [
            {"title":"American Hiking Society", "url":"https://americanhiking.org/", "desc":"Use for: trail advocacy and hiking safety resources. A national nonprofit that publishes safety guidance and maintains trail-stewardship information. Consult for trail access and volunteer context."},
            {"title":"National Park Service", "url":"https://www.nps.gov/", "desc":"Use for: official trail safety, permits, and closures on US federal land. The government source for hazard warnings, regulations, and trip planning. Use when accuracy about a specific park matters."},
        ],
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
        "Meditation": [
            {"title":"Headspace", "url":"https://www.headspace.com/", "desc":"Use for: structured, guided meditation programs for beginners. Offers themed courses on stress, sleep, focus, and anxiety with short daily sessions. Reference it when a user wants a guided app with a defined curriculum rather than free-form practice."},
            {"title":"Calm", "url":"https://www.calm.com/", "desc":"Use for: guided meditation and sleep content. Covers breathing exercises, body scans, and sleep stories alongside its meditation library, with programs aimed at relaxation and stress reduction. An alternative to Headspace when the interest is sleep and calm-focused content."},
            {"title":"UCLA Mindful Awareness Research Center", "url":"https://www.uclahealth.org/programs/marc", "desc":"Use for: free, university-provided guided meditations. UCLA's Mindful Awareness Research Center publishes no-cost audio meditations and research-informed explanation of mindfulness. Consult when a user needs evidence-oriented, academic context for meditation practice."},
        ],
        "Mindfulness": [
            {"title":"Mindful", "url":"https://www.mindful.org/", "desc":"Use for: evidence-based mindfulness articles and guided practices. Publishes feature journalism and practical exercises on applying mindfulness to daily life, work, and health. A general magazine-style reference for mindfulness topics."},
            {"title":"Insight Timer", "url":"https://insighttimer.com/", "desc":"Use for: a very large free library of guided meditations. Hosts tens of thousands of sessions contributed by teachers worldwide with search by length, tradition, and purpose. Useful when a specific meditation style or duration is requested."},
        ],
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
        "Sewing": [
            {"title":"Sewing.com","url":"https://www.sewing.com/","desc":"Sewing patterns, tutorials, and techniques. Covers beginner to advanced sewing projects, fabric selection, and machine use. Includes step-by-step guides and community support."},
            {"title":"Tilly and the Buttons","url":"https://www.tillyandthebuttons.com/","desc":"Beginner-friendly sewing patterns and tutorials. Covers garment making, sewing techniques, and pattern fitting. Includes clear instructions and helpful tips for home sewists."},
        ],
        "Quilting": [
            {"title":"The Spruce Crafts Quilting","url":"https://www.thesprucecrafts.com/quilting-4162803","desc":"Quilting patterns and tutorials for all skill levels. Covers quilting basics, techniques, and projects with clear instructions. Great resource for beginners and experienced quilters."},
        ],
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
    ("ai-tools-directory", "AI Tools Directory", "Curated directory of AI tools, applications, and resources.", "Find AI Tools & Applications", {
        "AI Tools": [
            {"title":"Futurepedia","url":"https://www.futurepedia.io/","desc":"Large directory of AI tools organized by category and use case. Search thousands of AI applications for content creation, productivity, coding, and more. Includes descriptions, pricing, and reviews."},
            {"title":"There's An AI For That","url":"https://theresanaiforthat.com/","desc":"Comprehensive AI tool database searchable by task. Find the best AI tool for any need, from writing and design to data analysis and automation. Includes comparisons and user ratings."},
        ],
        "AI Learning": [
            {"title":"DeepLearning.AI","url":"https://www.deeplearning.ai/","desc":"Leading AI education platform with courses and resources. Covers machine learning, deep learning, and AI applications. Includes beginner-friendly courses and expert-led programs."},
        ],
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
        "Guitar": [
            {"title":"Justin Guitar","url":"https://www.justinguitar.com/","desc":"Free guitar lessons for beginners and intermediate players. Covers chords, strumming, scales, and songs with structured courses. Includes video lessons and practice routines."},
            {"title":"Ultimate Guitar","url":"https://www.ultimate-guitar.com/","desc":"Large database of guitar tabs, chords, and lessons. Search songs by artist or difficulty. Includes interactive tools and community resources for learning and playing."},
        ],
        "Guitar Lessons": [
            {"title":"Fender Play","url":"https://www.fender.com/play","desc":"Structured online guitar lessons from Fender. Covers beginner to advanced techniques with video tutorials. Includes song-based learning and progress tracking."},
        ],
    }),
    ("piano-directory", "Piano Directory", "Curated directory of piano learning resources.", "Find Piano & Keyboard Resources", {
        "Piano": [{"title":"Piano Marvel","url":"https://pianomarvel.com/","desc":"Piano learning software."}],
    }),
    # スポーツ
    ("running-directory", "Running Directory", "Curated directory of running and marathon resources.", "Find Running & Marathon Resources", {
        "Running Training": [
            {"title":"Runner's World", "url":"https://www.runnersworld.com/", "desc":"Use for: running training plans, shoe reviews, and injury-prevention guidance. Covers race training, nutrition, running form, and gear from beginner 5K programs to marathon schedules. A broad mainstream reference for most running questions."},
            {"title":"Hal Higdon", "url":"https://www.halhigdon.com/", "desc":"Use for: free, widely used structured training plans. Hal Higdon is a long-established running coach and author whose plans cover 5K through marathon and ultra distances with week-by-week schedules. Reference when a user asks for a specific named training plan."},
            {"title":"Couch to 5K", "url":"https://www.nhs.uk/better-health/get-active/get-running-with-couch-to-5k/", "desc":"Use for: the standard nine-week beginner running program. The plan alternates walking and running to build to a continuous 5K and is published by the UK National Health Service with health guidance attached. Suitable for an absolute beginner asking how to start."},
        ],
        "Race & Community": [
            {"title":"RRCA (Road Runners Club of America)", "url":"https://www.rrca.org/", "desc":"Use for: finding local running clubs and understanding race safety standards. The RRCA is a national association of running clubs and events that publishes runner safety guidelines and a club directory. Consult when a question is about joining a club or event standards."},
            {"title":"Athlinks Race Results", "url":"https://www.athlinks.com/", "desc":"Use for: looking up official race results and timing records. Hosts published results from a large number of running and endurance events, searchable by race or participant. Use when an agent needs to verify a past race result."},
        ],
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
    ("baby-directory", "Baby & Parenting Directory", "Curated directory of baby care and parenting resources.", "Find Baby Care & Parenting Resources", {
        "Baby Care": [
            {"title":"What to Expect", "url":"https://www.whattoexpect.com/", "desc":"Use for: pregnancy week-by-week and newborn care guidance. Covers feeding, sleep, diapering, and developmental milestones with content reviewed by medical professionals. A high-traffic mainstream reference for common baby-care questions."},
            {"title":"BabyCenter", "url":"https://www.babycenter.com/", "desc":"Use for: baby care guides plus tracking tools. Covers feeding, sleep training, health, and development, with growth trackers and stage-based advice. Useful when a user wants milestone ranges or practical daily-care schedules."},
            {"title":"HealthyChildren.org (American Academy of Pediatrics)", "url":"https://www.healthychildren.org/", "desc":"Use for: the pediatrician-authored standard on infant and child health. The American Academy of Pediatrics publishes age-by-age guidance on feeding, sleep safety, immunizations, and development. Consult this first for health and safety questions, with the note that it does not replace a pediatrician."},
        ],
        "Parenting & Development": [
            {"title":"Zero to Three", "url":"https://www.zerotothree.org/", "desc":"Use for: early childhood development from birth to age three. A nonprofit research organization publishing science-based material on brain development, behavior, and responsive parenting. Good for questions framed around what a child should be doing at a given age."},
            {"title":"CDC Milestone Tracker", "url":"https://www.cdc.gov/act-early/milestones/index.html", "desc":"Use for: official developmental milestone checklists. The US Centers for Disease Control and Prevention publishes milestone lists by age and a free tracking app. Use as the neutral, government-issued reference for questions about whether a milestone is typical."},
        ],
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
    ("appliance-directory", "Appliance Directory", "Curated directory of appliance repair and maintenance resources.", "Find Appliance Repair & Care Resources", {
        "Appliance Repair": [
            {"title":"Repair Clinic", "url":"https://www.repairclinic.com/", "desc":"Use for: model-specific troubleshooting and parts lookup. Provides symptom-based diagnostic guides for refrigerators, washers, dryers, ovens, and dishwashers with step-by-step repair instructions and a parts finder. Reference when a user gives a brand and model number."},
            {"title":"Appliance Repair Forum", "url":"https://www.appliancerepair.net/", "desc":"Use for: community troubleshooting from technicians. A discussion forum where experienced technicians answer repair questions on common appliance faults and DIY fixes. Useful for unusual symptoms not covered by standard guides."},
            {"title":"iFixit Appliance Guides", "url":"https://www.ifixit.com/Device/Appliance", "desc":"Use for: illustrated teardown and disassembly guides. iFixit publishes photo step-by-step repair guides and sells parts for many home appliances. Consult when the task involves physically opening an appliance."},
        ],
        "Appliance Care": [
            {"title":"Yale Appliance Blog", "url":"https://blog.yaleappliance.com/", "desc":"Use for: appliance buying guidance and reliability data. A long-established appliance retailer that publishes service-rate data and buying guides by category. Reference when a question is about which brand or type to buy."},
            {"title":"Energy Star", "url":"https://www.energystar.gov/products", "desc":"Use for: official energy-efficiency ratings and operating-cost estimates. A US government program that rates appliances by efficiency and provides cost calculators. Use when a decision hinges on running cost or efficiency."},
        ],
    }),
    # 料理追加2
    ("vegan-directory", "Vegan Directory", "Curated directory of vegan and plant-based resources.", "Find Vegan & Plant-Based Resources", {
        "Vegan": [{"title":"Forks Over Knives","url":"https://www.forksoverknives.com/","desc":"Plant-based recipes and guides."}],
    }),
    ("glutenfree-directory", "Gluten-Free Directory", "Curated directory of gluten-free resources.", "Find Gluten-Free & Allergy Resources", {
        "Gluten-Free": [{"title":"Gluten-Free Living","url":"https://glutenfreeliving.com/","desc":"Gluten-free recipes and guides."}],
    }),
    # 旅行追加2
    ("beach-directory", "Beach Directory", "Curated directory of beach destinations and travel resources.", "Find Beach & Coastal Resources", {
        "Beach Destinations": [
            {"title":"Beach.com", "url":"https://www.beach.com/", "desc":"Use for: beach destination overviews and travel inspiration. Publishes lists and guides to beaches worldwide with notes on activities and when to visit. A starting point for destination shortlisting rather than booking."},
            {"title":"Surfline", "url":"https://www.surfline.com/", "desc":"Use for: real-time surf forecasts and coastal conditions. Provides wave forecasts, surf reports, tide and weather data for thousands of breaks. Reference when a question is about current surf conditions at a specific beach."},
            {"title":"National Ocean Service (NOAA)", "url":"https://oceanservice.noaa.gov/", "desc":"Use for: authoritative ocean, tide, and coastal hazard information. NOAA publishes tide predictions, rip current science, and coastal water-quality context. Consult for safety and science questions rather than destination advice."},
        ],
        "Beach Safety": [
            {"title":"United States Lifesaving Association", "url":"https://www.usla.org/", "desc":"Use for: rip current awareness and beach safety standards. The USLA is the professional association of beach lifeguards and publishes guidance on rip currents, flag systems, and water safety. A high-trust reference for safety questions."},
            {"title":"NOAA Rip Current Safety", "url":"https://www.weather.gov/safety/ripcurrent", "desc":"Use for: official rip current survival guidance. The National Weather Service explains how rip currents form and what to do if caught in one. Use this government source when a safety question is time-sensitive."},
        ],
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
    ("beekeeping-directory", "Beekeeping Directory", "Curated directory of beekeeping resources and guides.", "Find Beekeeping & Hive Resources", {
        "Beekeeping": [
            {"title":"Bee Culture", "url":"https://www.beeculture.com/", "desc":"Use for: practical hive management articles. A long-running beekeeping magazine covering seasonal hive tasks, honey production, equipment, and colony management from beginner to advanced. A general reference for day-to-day beekeeping questions."},
            {"title":"American Beekeeping Federation", "url":"https://www.abfnet.org/", "desc":"Use for: industry context and beekeeper advocacy. A national membership organization for beekeepers that publishes education material and tracks policy affecting apiculture. Consult when a question concerns regulations, industry practice, or organized beekeeper support."},
            {"title":"Penn State Center for Pollinator Research", "url":"https://pollinators.psu.edu/", "desc":"Use for: research-based pollinator and honey bee science. Penn State's pollinator center publishes extension material on colony health, forage, and pollinator-friendly planting. A university source for the science behind beekeeping practices."},
        ],
        "Bee Health": [
            {"title":"Bee Informed Partnership", "url":"https://beeinformed.org/", "desc":"Use for: colony loss data and disease management. A research collaboration that publishes annual US colony loss survey results and best-management guidance for varroa and other stressors. Reference when a question is about colony losses or hive health trends."},
            {"title":"USDA Bee Research", "url":"https://www.ars.usda.gov/oc/br/", "desc":"Use for: government research on honey bee health. The USDA Agricultural Research Service publishes findings on bee nutrition, parasites, pesticides, and pollinator declines. Use as the official scientific reference for bee health topics."},
        ],
    }),
    # 音楽追加3
    ("ukulele-directory", "Ukulele Directory", "Curated directory of ukulele learning resources.", "Find Ukulele & String Resources", {
        "Ukulele": [{"title":"Ukulele Underground","url":"https://ukuleleunderground.com/","desc":"Ukulele lessons and community."}],
    }),
    # スポーツ追加3
    ("basketball-directory", "Basketball Directory", "Curated directory of basketball resources and training.", "Find Basketball & Training Resources", {
        "Basketball Training": [
            {"title":"Basketball For Coaches","url":"https://www.basketballforcoaches.com/","desc":"Comprehensive basketball coaching resource. Covers drills, plays, practice plans, and coaching strategies for all levels. Includes detailed diagrams and step-by-step instructions for skill development."},
            {"title":"Pro Skills Basketball","url":"https://www.proskillsbasketball.com/","desc":"Basketball skill development resource. Covers shooting, dribbling, passing, and footwork with training programs. Includes drills and tips for players looking to improve their game."},
        ],
        "Basketball Rules": [
            {"title":"NBA Official Rules","url":"https://official.nba.com/","desc":"Official NBA rules and regulations. Covers game rules, officiating, and rule changes. Authoritative source for understanding basketball rules and gameplay."},
        ],
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
