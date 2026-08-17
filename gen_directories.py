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
            {"title":"AKC Training","url":"https://www.akc.org/expert-advice/training/","desc":"Official American Kennel Club dog training guides. Step-by-step articles on obedience commands (sit, stay, come, heel), potty training, crate training, leash walking, and correcting common behavior problems like barking, jumping, and chewing. Authoritative source from the leading purebred dog registry in the US."},
            {"title":"The Spruce Pets Training","url":"https://www.thesprucepets.com/dog-training-4162107","desc":"Comprehensive dog training resource with beginner-friendly tutorials. Covers positive reinforcement methods, clicker training, puppy socialization, and how to fix behavioral issues. Includes age-specific advice from puppyhood to senior dogs and practical step-by-step routines."},
        ],
        "Dog Health": [
            {"title":"Vetstreet","url":"https://www.vetstreet.com/","desc":"Veterinary-reviewed dog health information. Articles on common canine diseases, symptoms to watch for, vaccination schedules, parasite prevention, dental care, and senior dog health. Written and reviewed by licensed veterinarians for accurate, reliable advice."},
            {"title":"AKC Health Resources","url":"https://www.akc.org/expert-advice/health/","desc":"American Kennel Club health articles covering breed-specific health concerns, genetic testing, nutrition, weight management, and preventive care. Includes information on common conditions like hip dysplasia, allergies, and heart disease with signs to watch for."},
        ],
    }),
    ("cat-care-directory", "Cat Care Directory", "Curated directory of cat care resources, health, and products.", "Find Cat Care & Health Resources", {
        "Cat Health": [
            {"title":"Cornell Feline Health Center","url":"https://www.vet.cornell.edu/","desc":"Cornell University's authoritative feline health resource. Research-backed articles on common cat diseases (FIV, feline leukemia, kidney disease), vaccination schedules, parasite prevention, and when to see a vet. Trusted by veterinarians worldwide for accurate, science-based cat health information."},
            {"title":"International Cat Care","url":"https://icatcare.org/","desc":"Global feline welfare charity providing expert cat health advice. Covers cat behavior, nutrition, common illnesses, and preventive care. Includes clear guides on symptoms, treatments, and understanding your cat's needs at every life stage."},
        ],
        "Cat Nutrition": [
            {"title":"PetMD Cat Nutrition","url":"https://www.petmd.com/cat/nutrition","desc":"Veterinary-reviewed cat nutrition guides. Explains wet vs dry food, portion sizes, age-specific dietary needs (kitten, adult, senior), and how to manage weight, allergies, and sensitive stomachs. Practical feeding advice from licensed veterinarians."},
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
            {"title":"REI Expert Advice","url":"https://www.rei.com/learn","desc":"Outdoor retailer's expert advice on camping and gear. Covers tent setup, sleeping systems, camp cooking, safety, and gear selection. Includes detailed guides for beginners and experienced campers."},
            {"title":"The Dyrt","url":"https://thedyrt.com/","desc":"Campground directory with user reviews and photos. Search thousands of campsites, read real camper experiences, and find the perfect spot. Includes tips on camping etiquette and planning."},
        ],
        "Outdoor Skills": [
            {"title":"Outdoor Life","url":"https://www.outdoorlife.com/","desc":"Outdoor and survival skills resource. Covers camping, fishing, hunting, and wilderness survival techniques. Practical guides for outdoor enthusiasts of all levels."},
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
            {"title":"EatRight","url":"https://www.eatright.org/","desc":"Academy of Nutrition and Dietetics official resource. Evidence-based nutrition information on healthy eating, weight management, and dietary guidelines. Trusted advice from registered dietitians."},
            {"title":"Nutrition.gov","url":"https://www.nutrition.gov/","desc":"US government nutrition resource with science-based information. Covers healthy eating, food safety, dietary supplements, and nutrition for all life stages. Reliable, authoritative source."},
        ],
        "Healthy Eating": [
            {"title":"Harvard Nutrition Source","url":"https://www.hsph.harvard.edu/nutritionsource/","desc":"Harvard School of Public Health nutrition resource. Research-backed articles on healthy eating, diet quality, and disease prevention. Includes the Healthy Eating Plate and evidence-based guidance."},
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
            {"title":"Ravelry","url":"https://www.ravelry.com/","desc":"Largest knitting and crochet community with millions of patterns. Search by yarn, difficulty, and project type. Includes forums, project galleries, and tools for tracking your work."},
            {"title":"KnittingHelp","url":"https://www.knittinghelp.com/","desc":"Free knitting tutorials with video demonstrations. Covers basic stitches, techniques, and pattern reading. Beginner-friendly resource for learning and improving knitting skills."},
        ],
        "Crochet": [
            {"title":"The Spruce Crafts Crochet","url":"https://www.thesprucecrafts.com/crochet-4162801","desc":"Crochet patterns and tutorials for all skill levels. Covers basic stitches, projects, and techniques with clear instructions and photos. Great resource for beginners and experienced crocheters."},
        ],
    }),
    ("woodworking-directory", "Woodworking Directory", "Curated directory of woodworking resources and projects.", "Find Woodworking & Craft Resources", {
        "Woodworking": [
            {"title":"Wood Magazine","url":"https://www.woodmagazine.com/","desc":"Woodworking projects, plans, and techniques. Covers furniture building, joinery, finishing, and tool guides. Includes step-by-step project plans for woodworkers of all skill levels."},
            {"title":"Fine Woodworking","url":"https://www.finewoodworking.com/","desc":"Advanced woodworking resource with expert techniques and detailed plans. Covers joinery, carving, finishing, and furniture design. Trusted by professional and serious hobbyist woodworkers."},
        ],
        "Woodworking Plans": [
            {"title":"Ana White","url":"https://www.ana-white.com/","desc":"Free DIY furniture plans with step-by-step instructions. Covers beginner-friendly projects using common lumber. Includes cut lists, diagrams, and building tips for home woodworkers."},
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
        "Coffee": [
            {"title":"Home-Barista","url":"https://www.home-barista.com/","desc":"Coffee brewing community and resource. Covers espresso, pour-over, and brewing techniques. Includes equipment reviews, troubleshooting, and expert advice for home coffee enthusiasts."},
            {"title":"Perfect Daily Grind","url":"https://perfectdailygrind.com/","desc":"Coffee industry news and brewing guides. Covers coffee science, brewing methods, and specialty coffee trends. Trusted resource for understanding coffee quality and preparation."},
        ],
        "Brewing": [
            {"title":"James Hoffmann","url":"https://www.jameshoffmann.co.uk/","desc":"Coffee expert with detailed brewing guides and reviews. Covers brewing techniques, equipment, and coffee science. Includes video tutorials and practical advice for better coffee."},
        ],
    }),
    ("wine-directory", "Wine Directory", "Curated directory of wine resources and tasting.", "Find Wine & Tasting Resources", {
        "Wine": [{"title":"Wine Spectator","url":"https://www.winespectator.com/","desc":"Wine reviews and tasting guides."}],
    }),
    # 旅行追加
    ("hiking-directory", "Hiking Directory", "Curated directory of hiking trails and outdoor resources.", "Find Hiking & Trail Resources", {
        "Hiking": [
            {"title":"AllTrails","url":"https://www.alltrails.com/","desc":"Hiking trail directory with user reviews and maps. Search thousands of trails by difficulty, length, and location. Includes photos, GPS tracks, and trail conditions from real hikers."},
            {"title":"REI Hiking Expert Advice","url":"https://www.rei.com/learn/expert-advice/hiking.html","desc":"Hiking gear and technique guides from REI. Covers trail planning, navigation, safety, and gear selection. Includes beginner-friendly advice for planning your first hike."},
        ],
        "Trail Guides": [
            {"title":"The Hiking Project","url":"https://www.hikingproject.com/","desc":"Community-driven trail database with detailed trail information. Covers trail difficulty, elevation, and conditions. Includes maps and user-contributed trail reports."},
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
            {"title":"Headspace","url":"https://www.headspace.com/","desc":"Guided meditation and mindfulness app with structured programs. Covers meditation basics, stress reduction, sleep, and focus. Includes beginner-friendly techniques for building a consistent practice."},
            {"title":"Calm","url":"https://www.calm.com/","desc":"Meditation and sleep resource with guided sessions. Covers mindfulness, breathing exercises, and sleep stories. Includes programs for stress, anxiety, and relaxation."},
        ],
        "Mindfulness": [
            {"title":"Mindful","url":"https://www.mindful.org/","desc":"Mindfulness resource with articles, guided practices, and research. Covers mindfulness techniques, stress management, and everyday applications. Trusted source for evidence-based mindfulness."},
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
        "Running": [
            {"title":"Runner's World","url":"https://www.runnersworld.com/","desc":"Running training plans, gear reviews, and expert advice. Covers marathon training, injury prevention, nutrition, and running techniques. Trusted resource for runners of all levels."},
            {"title":"Hal Higdon","url":"https://www.halhigdon.com/","desc":"Renowned running coach with free training plans. Covers beginner to advanced marathon, half-marathon, and 5K programs. Includes detailed schedules and training advice."},
        ],
        "Running Plans": [
            {"title":"Couch to 5K","url":"https://www.c25k.com/","desc":"Beginner running program that takes you from couch to 5K in 9 weeks. Covers interval training and gradual progression. Includes structured plans for new runners."},
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
            {"title":"What to Expect","url":"https://www.whattoexpect.com/","desc":"Trusted pregnancy and baby care resource. Covers pregnancy week-by-week, newborn care, feeding, sleep, and developmental milestones. Includes expert-reviewed articles and community support."},
            {"title":"BabyCenter","url":"https://www.babycenter.com/","desc":"Comprehensive parenting resource with baby care guides. Covers feeding, sleep training, health, and development. Includes tools like growth trackers and expert advice for every stage."},
        ],
        "Parenting": [
            {"title":"Zero to Three","url":"https://www.zerotothree.org/","desc":"Early childhood development resource. Science-based information on child development, behavior, and parenting from birth to age three. Trusted by parents and professionals."},
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
            {"title":"Repair Clinic","url":"https://www.repairclinic.com/","desc":"Appliance repair resource with troubleshooting guides and parts. Covers refrigerators, washers, dryers, ovens, and more. Includes step-by-step repair instructions and a parts lookup tool."},
            {"title":"Appliance Repair Forum","url":"https://www.appliancerepair.net/","desc":"Community forum for appliance repair help. Ask questions and get answers from experienced technicians. Covers common appliance problems and DIY repair solutions."},
        ],
        "Appliance Care": [
            {"title":"Yale Appliance","url":"https://www.yaleappliance.com/","desc":"Appliance buying and maintenance guides. Covers how to choose appliances, care tips, and common problems. Includes expert advice on extending appliance lifespan."},
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
            {"title":"Beach.com","url":"https://www.beach.com/","desc":"Beach destination guides and travel inspiration. Covers top beaches worldwide, activities, and travel tips. Includes information on the best times to visit and what to expect."},
            {"title":"Surfline","url":"https://www.surfline.com/","desc":"Surf and beach conditions resource. Real-time wave forecasts, surf reports, and beach weather. Useful for surfers and beachgoers planning coastal activities."},
        ],
        "Beach Safety": [
            {"title":"United States Lifesaving Association","url":"https://www.usla.org/","desc":"Beach safety resource with rip current awareness and drowning prevention. Covers beach flags, water safety, and lifeguard information. Authoritative source for safe beach practices."},
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
            {"title":"Bee Culture","url":"https://www.beeculture.com/","desc":"Leading beekeeping magazine with articles on hive management, honey production, and bee health. Covers beginner to advanced beekeeping techniques, equipment, and seasonal tasks."},
            {"title":"American Beekeeping Federation","url":"https://www.abfnet.org/","desc":"National beekeeping organization with resources for beekeepers. Covers education, advocacy, and best practices. Includes information on bee health, regulations, and community support."},
        ],
        "Bee Health": [
            {"title":"Bee Informed Partnership","url":"https://beeinformed.org/","desc":"Research-based resource on honey bee health. Covers colony loss data, disease management, and best practices. Trusted source for understanding and protecting bee colonies."},
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
