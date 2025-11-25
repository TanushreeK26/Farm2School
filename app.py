from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = 'farm2school_secret_key'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'susmitha.vcsc@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_app_password'  # Replace with actual app password
app.config['MAIL_DEFAULT_SENDER'] = 'susmitha.vcsc@gmail.com'

mail = Mail(app)

# MongoDB configuration
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['farm2school']
    users = db['users']
    products = db['products']
    orders = db['orders']
    messages = db['messages']
    print("MongoDB connected successfully")
except Exception as e:
    print(f"MongoDB connection error: {str(e)}")

# Translations
translations = {
    'en': {
        'title': 'Farm2School - Connecting Farms to Schools',
        'tagline': 'Fresh • Local • Sustainable',
        'nav': {
            'home': 'Home',
            'about': 'About',
            'how_it_works': 'How It Works',
            'features': 'Features',
            'contact': 'Contact',
            'login': 'Login',
            'register': 'Register'
        },
        'hero': {
            'title': 'Connecting Fresh Farms to Schools',
            'subtitle': 'Building healthier communities by connecting local farms with schools',
            'get_started': 'Get Started',
            'learn_more': 'Learn More'
        },
        'about': {
            'title': 'About Farm2School',
            'subtitle': 'Building healthier communities by connecting local farms with schools',
            'description1': 'Farm2School is a revolutionary platform that bridges the gap between local farmers and educational institutions. We believe in providing students with access to fresh, nutritious, and locally-sourced food while supporting small-scale farmers in our communities.',
            'description2': 'Our mission is to create sustainable food systems that benefit everyone involved - farmers get fair prices for their produce, schools receive fresh ingredients, and students enjoy healthier meals that contribute to their overall well-being.'
        },
        'how_it_works': {
            'title': 'How It Works',
            'subtitle': 'A simple process connecting farms to schools',
            'step1': {'title': 'Register', 'description': 'Farmers and schools create accounts on our platform with their details and requirements.'},
            'step2': {'title': 'List & Browse', 'description': 'Farmers list their available produce, and schools browse through the available options.'},
            'step3': {'title': 'Order', 'description': 'Schools place orders for the fresh produce they need directly from local farmers.'},
            'step4': {'title': 'Deliver', 'description': 'Farmers deliver fresh produce to schools, and payments are processed securely.'}
        },
        'features': {
            'title': 'Platform Features',
            'subtitle': 'Tools designed to make farm-to-school connections seamless',
            'feature1': {'title': 'Fresh Produce', 'description': 'Access to the freshest locally-grown fruits, vegetables, and dairy products.'},
            'feature2': {'title': 'Direct Connection', 'description': 'Eliminate middlemen and connect directly with local farmers and schools.'},
            'feature3': {'title': 'Real-time Tracking', 'description': 'Track orders from placement to delivery with our real-time tracking system.'},
            'feature4': {'title': 'Sustainability', 'description': 'Promote environmentally-friendly practices and reduce food miles.'},
            'feature5': {'title': 'Educational Resources', 'description': 'Access educational materials about farming, nutrition, and sustainability.'},
            'feature6': {'title': 'Mobile Friendly', 'description': 'Access the platform from any device with our responsive design.'}
        },
        'contact': {
            'title': 'Contact Us',
            'subtitle': 'Have questions? We\'d love to hear from you',
            'address': {'title': 'Address', 'value': 'Thudiyalur, Coimbatore'},
            'phone': {'title': 'Phone'},
            'email': {'title': 'Email'},
            'form': {'name': 'Your Name', 'email': 'Your Email', 'message': 'Your Message', 'send': 'Send Message'}
        },
        'footer': {
            'tagline': 'Connecting farms to schools for a healthier future',
            'quick_links': 'Quick Links',
            'follow_us': 'Follow Us',
            'rights': 'All rights reserved.'
        },
        'login': {
            'title': 'Welcome Back',
            'subtitle': 'Login to your Farm2School account',
            'email': 'Email Address',
            'password': 'Password',
            'remember': 'Remember me',
            'forgot': 'Forgot password?',
            'login_btn': 'Login',
            'no_account': "Don't have an account?",
            'register_here': 'Register here'
        },
        'register': {
            'title': 'Create Account',
            'subtitle': 'Join Farm2School to connect farms and schools',
            'user_type': 'I am a:',
            'farmer': 'Farmer',
            'farmer_desc': 'I want to sell my produce',
            'school': 'School',
            'school_desc': 'I want to buy fresh produce',
            'name': 'Name',
            'email': 'Email Address',
            'district': 'District',
            'location': 'Specific Location/Address',
            'password': 'Password',
            'register_btn': 'Register',
            'have_account': 'Already have an account?',
            'login_here': 'Login here'
        },
        'dashboard': {
            'farmer': {
                'title': 'Farmer Dashboard',
                'schools_in_district': 'Schools in Your District',
                'your_products': 'Your Products',
                'orders': 'Orders',
                'add_product': 'Add Product',
                'product_name': 'Product Name',
                'description': 'Description',
                'price': 'Price (₹)',
                'quantity': 'Quantity (in kgs)',
                'category': 'Category',
                'contact': 'Contact',
                'delete': 'Delete',
                'out_of_stock': 'Out of Stock'
            },
            'school': {
                'title': 'School Dashboard',
                'farmers_in_district': 'Farmers in Your District',
                'available_products': 'Available Products',
                'your_orders': 'Your Orders',
                'order': 'Order',
                'filter': 'Filter',
                'clear': 'Clear'
            },
            'common': {
                'home': 'Home',
                'dashboard': 'Dashboard',
                'messages': 'Messages',
                'analytics': 'Analytics',
                'logout': 'Logout',
                'products_listed': 'Products Listed',
                'total_orders': 'Total Orders',
                'delivered_orders': 'Delivered Orders'
            }
        }
    },
    'ta': {
        'title': 'Farm2School - பண்ணைகளை பள்ளிகளுடன் இணைக்கிறது',
        'tagline': 'புதிய • உள்ளூர் • நிலையான',
        'nav': {
            'home': 'முகப்பு',
            'about': 'எங்களைப் பற்றி',
            'how_it_works': 'எப்படி வேலை செய்கிறது',
            'features': 'அம்சங்கள்',
            'contact': 'தொடர்பு',
            'login': 'உள்நுழைய',
            'register': 'பதிவு செய்ய'
        },
        'hero': {
            'title': 'புதிய பண்ணைகளை பள்ளிகளுடன் இணைக்கிறது',
            'subtitle': 'உள்ளூர் பண்ணைகளை பள்ளிகளுடன் இணைத்து ஆரோக்கியமான சமுதாயங்களை உருவாக்குதல்',
            'get_started': 'தொடங்குங்கள்',
            'learn_more': 'மேலும் அறிய'
        },
        'about': {
            'title': 'Farm2School பற்றி',
            'subtitle': 'உள்ளூர் பண்ணைகளை பள்ளிகளுடன் இணைத்து ஆரோக்கியமான சமுதாயங்களை உருவாக்குதல்',
            'description1': 'Farm2School என்பது உள்ளூர் விவசாயிகளுக்கும் கல்வி நிறுவனங்களுக்கும் இடையிலான இடைவெளியைக் குறைக்கும் ஒரு புரட்சிகர தளமாகும். எங்கள் சமுதாயங்களில் உள்ள சிறிய அளவிலான விவசாயிகளை ஆதரிக்கும் அதே வேளையில் மாணவர்களுக்கு புதிய, சத்தான மற்றும் உள்ளூர் உணவுகளை வழங்குவதில் நாங்கள் நம்புகிறோம்.',
            'description2': 'சம்பந்தப்பட்ட அனைவருக்கும் பயனளிக்கும் நிலையான உணவு அமைப்புகளை உருவாக்குவதே எங்கள் நோக்கம் - விவசாயிகள் தங்கள் விளைபொருட்களுக்கு நியாயமான விலையைப் பெறுகிறார்கள், பள்ளிகள் புதிய பொருட்களைப் பெறுகின்றன, மாணவர்கள் அவர்களின் ஒட்டுமொத்த நல்வாழ்வுக்கு பங்களிக்கும் ஆரோக்கியமான உணவுகளை அனுபவிக்கிறார்கள்.'
        },
        'how_it_works': {
            'title': 'எப்படி வேலை செய்கிறது',
            'subtitle': 'பண்ணைகளை பள்ளிகளுடன் இணைக்கும் எளிய செயல்முறை',
            'step1': {'title': 'பதிவு செய்ய', 'description': 'விவசாயிகள் மற்றும் பள்ளிகள் தங்கள் விவரங்கள் மற்றும் தேவைகளுடன் எங்கள் தளத்தில் கணக்குகளை உருவாக்குகின்றன.'},
            'step2': {'title': 'பட்டியல் மற்றும் உலாவல்', 'description': 'விவசாயிகள் தங்கள் கிடைக்கக்கூடிய விளைபொருட்களை பட்டியலிடுகிறார்கள், பள்ளிகள் கிடைக்கக்கூடிய விருப்பங்களை உலாவுகின்றன.'},
            'step3': {'title': 'ஆர்டர்', 'description': 'பள்ளிகள் உள்ளூர் விவசாயிகளிடமிருந்து நேரடியாக தங்களுக்குத் தேவையான புதிய விளைபொருட்களுக்கு ஆர்டர் செய்கின்றன.'},
            'step4': {'title': 'விநியோகம்', 'description': 'விவசாயிகள் பள்ளிகளுக்கு புதிய விளைபொருட்களை வழங்குகிறார்கள், பணம் செலுத்துதல் பாதுகாப்பாக செயல்படுத்தப்படுகிறது.'}
        },
        'features': {
            'title': 'தள அம்சங்கள்',
            'subtitle': 'பண்ணை-பள்ளி இணைப்புகளை தடையற்றதாக மாற்ற வடிவமைக்கப்பட்ட கருவிகள்',
            'feature1': {'title': 'புதிய விளைபொருட்கள்', 'description': 'புதிய உள்ளூர் பழங்கள், காய்கறிகள் மற்றும் பால் பொருட்களை அணுகுதல்.'},
            'feature2': {'title': 'நேரடி இணைப்பு', 'description': 'இடைத்தரகர்களை நீக்கி உள்ளூர் விவசாயிகள் மற்றும் பள்ளிகளுடன் நேரடியாக இணைக்கவும்.'},
            'feature3': {'title': 'நிகழ்நேர கண்காணிப்பு', 'description': 'எங்கள் நிகழ்நேர கண்காணிப்பு அமைப்புடன் ஆர்டர் செய்வதிலிருந்து விநியோகம் வரை கண்காணிக்கவும்.'},
            'feature4': {'title': 'நிலைத்தன்மை', 'description': 'சுற்றுச்சூழல் நட்பு நடைமுறைகளை ஊக்குவித்து உணவு மைல்களை குறைக்கவும்.'},
            'feature5': {'title': 'கல்வி வளங்கள்', 'description': 'விவசாயம், ஊட்டச்சத்து மற்றும் நிலைத்தன்மை பற்றிய கல்வி பொருட்களை அணுகவும்.'},
            'feature6': {'title': 'மொபைல் நட்பு', 'description': 'எங்கள் பதிலளிக்கக்கூடிய வடிவமைப்புடன் எந்த சாதனத்திலிருந்தும் தளத்தை அணுகவும்.'}
        },
        'contact': {
            'title': 'எங்களை தொடர்பு கொள்ளுங்கள்',
            'subtitle': 'கேள்விகள் உள்ளதா? உங்களிடமிருந்து கேட்க விரும்புகிறோம்',
            'address': {'title': 'முகவரி', 'value': 'துடியலூர், கோயம்புத்தூர்'},
            'phone': {'title': 'தொலைபேசி'},
            'email': {'title': 'மின்னஞ்சல்'},
            'form': {'name': 'உங்கள் பெயர்', 'email': 'உங்கள் மின்னஞ்சல்', 'message': 'உங்கள் செய்தி', 'send': 'செய்தி அனுப்பு'}
        },
        'footer': {
            'tagline': 'ஆரோக்கியமான எதிர்காலத்திற்காக பண்ணைகளை பள்ளிகளுடன் இணைக்கிறது',
            'quick_links': 'விரைவு இணைப்புகள்',
            'follow_us': 'எங்களை பின்தொடருங்கள்',
            'rights': 'அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை.'
        },
        'login': {
            'title': 'மீண்டும் வரவேற்கிறோம்',
            'subtitle': 'உங்கள் Farm2School கணக்கில் உள்நுழையுங்கள்',
            'email': 'மின்னஞ்சல் முகவரி',
            'password': 'கடவுச்சொல்',
            'remember': 'என்னை நினைவில் வைத்துக்கொள்ளுங்கள்',
            'forgot': 'கடவுச்சொல் மறந்துவிட்டதா?',
            'login_btn': 'உள்நுழைய',
            'no_account': 'கணக்கு இல்லையா?',
            'register_here': 'இங்கே பதிவு செய்யுங்கள்'
        },
        'register': {
            'title': 'கணக்கு உருவாக்கவும்',
            'subtitle': 'பண்ணைகளை பள்ளிகளுடன் இணைக்க Farm2School இல் சேருங்கள்',
            'user_type': 'நான் ஒரு:',
            'farmer': 'விவசாயி',
            'farmer_desc': 'நான் என் விளைபொருட்களை விற்க விரும்புகிறேன்',
            'school': 'பள்ளி',
            'school_desc': 'நான் புதிய விளைபொருட்களை வாங்க விரும்புகிறேன்',
            'name': 'பெயர்',
            'email': 'மின்னஞ்சல் முகவரி',
            'district': 'மாவட்டம்',
            'location': 'குறிப்பிட்ட இடம்/முகவரி',
            'password': 'கடவுச்சொல்',
            'register_btn': 'பதிவு செய்யுங்கள்',
            'have_account': 'ஏற்கனவே கணக்கு உள்ளதா?',
            'login_here': 'இங்கே உள்நுழையுங்கள்'
        },
        'dashboard': {
            'farmer': {
                'title': 'விவசாயி டாஷ்போர்டு',
                'schools_in_district': 'உங்கள் மாவட்டத்தில் உள்ள பள்ளிகள்',
                'your_products': 'உங்கள் பொருட்கள்',
                'orders': 'ஆர்டர்கள்',
                'add_product': 'பொருள் சேர்க்கவும்',
                'product_name': 'பொருளின் பெயர்',
                'description': 'விளக்கம்',
                'price': 'விலை (₹)',
                'quantity': 'அளவு (கிலோவில்)',
                'category': 'வகை',
                'contact': 'தொடர்பு',
                'delete': 'நீக்கு',
                'out_of_stock': 'கையிருப்பு இல்லை'
            },
            'school': {
                'title': 'பள்ளி டாஷ்போர்டு',
                'farmers_in_district': 'உங்கள் மாவட்டத்தில் உள்ள விவசாயிகள்',
                'available_products': 'கிடைக்கும் பொருட்கள்',
                'your_orders': 'உங்கள் ஆர்டர்கள்',
                'order': 'ஆர்டர்',
                'filter': 'வடிகட்டு',
                'clear': 'அழிக்கவும்'
            },
            'common': {
                'home': 'முகப்பு',
                'dashboard': 'டாஷ்போர்டு',
                'messages': 'செய்திகள்',
                'analytics': 'பகுப்பாய்வு',
                'logout': 'வெளியேறு',
                'products_listed': 'பட்டியலிடப்பட்ட பொருட்கள்',
                'total_orders': 'மொத்த ஆர்டர்கள்',
                'delivered_orders': 'வழங்கப்பட்ட ஆர்டர்கள்'
            }
        }
    },
    'hi': {
        'title': 'Farm2School - खेतों को स्कूलों से जोड़ना',
        'tagline': 'ताज़ा • स्थानीय • टिकाऊ',
        'nav': {
            'home': 'होम',
            'about': 'हमारे बारे में',
            'how_it_works': 'यह कैसे काम करता है',
            'features': 'विशेषताएं',
            'contact': 'संपर्क',
            'login': 'लॉगिन',
            'register': 'रजिस्टर'
        },
        'hero': {
            'title': 'ताज़े खेतों को स्कूलों से जोड़ना',
            'subtitle': 'स्थानीय खेतों को स्कूलों से जोड़कर स्वस्थ समुदाय बनाना',
            'get_started': 'शुरू करें',
            'learn_more': 'और जानें'
        },
        'about': {
            'title': 'Farm2School के बारे में',
            'subtitle': 'स्थानीय खेतों को स्कूलों से जोड़कर स्वस्थ समुदाय बनाना',
            'description1': 'Farm2School एक क्रांतिकारी प्लेटफॉर्म है जो स्थानीय किसानों और शैक्षणिक संस्थानों के बीच की खाई को पाटता है। हम छात्रों को ताज़े, पौष्टिक और स्थानीय रूप से उगाए गए भोजन तक पहुंच प्रदान करने में विश्वास करते हैं जबकि हमारे समुदायों में छोटे पैमाने के किसानों का समर्थन करते हैं।',
            'description2': 'हमका मिशन टिकाऊ खाद्य प्रणालियां बनाना है जो सभी शामिल लोगों को लाभ पहुंचाती हैं - किसानों को उनकी उपज के लिए उचित मूल्य मिलता है, स्कूलों को ताज़ी सामग्री मिलती है, और छात्र स्वस्थ भोजन का आनंद लेते हैं जो उनकी समग्र भलाई में योगदान देता है।'
        },
        'how_it_works': {
            'title': 'यह कैसे काम करता है',
            'subtitle': 'खेतों को स्कूलों से जोड़ने की एक सरल प्रक्रिया',
            'step1': {'title': 'रजिस्टर करें', 'description': 'किसान और स्कूल अपने विवरण और आवश्यकताओं के साथ हमारे प्लेटफॉर्म पर खाते बनाते हैं।'},
            'step2': {'title': 'सूची और ब्राउज़', 'description': 'किसान अपनी उपलब्ध उपज की सूची बनाते हैं, और स्कूल उपलब्ध विकल्पों को ब्राउज़ करते हैं।'},
            'step3': {'title': 'ऑर्डर', 'description': 'स्कूल स्थानीय किसानों से सीधे अपनी आवश्यक ताज़ी उपज के लिए ऑर्डर देते हैं।'},
            'step4': {'title': 'डिलीवरी', 'description': 'किसान स्कूलों को ताज़ी उपज पहुंचाते हैं, और भुगतान सुरक्षित रूप से संसाधित होता है।'}
        },
        'features': {
            'title': 'प्लेटफॉर्म विशेषताएं',
            'subtitle': 'खेत-से-स्कूल कनेक्शन को निर्बाध बनाने के लिए डिज़ाइन किए गए उपकरण',
            'feature1': {'title': 'ताज़ी उपज', 'description': 'सबसे ताज़े स्थानीय रूप से उगाए गए फल, सब्जियां और डेयरी उत्पादों तक पहुंच।'},
            'feature2': {'title': 'प्रत्यक्ष कनेक्शन', 'description': 'बिचौलियों को हटाएं और स्थानीय किसानों और स्कूलों से सीधे जुड़ें।'},
            'feature3': {'title': 'रियल-टाइम ट्रैकिंग', 'description': 'हमारे रियल-टाइम ट्रैकिंग सिस्टम के साथ ऑर्डर प्लेसमेंट से डिलीवरी तक ट्रैक करें।'},
            'feature4': {'title': 'स्थिरता', 'description': 'पर्यावरण-अनुकूल प्रथाओं को बढ़ावा दें और खाद्य मील कम करें।'},
            'feature5': {'title': 'शैक्षिक संसाधन', 'description': 'खेती, पोषण और स्थिरता के बारे में शैक्षिक सामग्री तक पहुंच।'},
            'feature6': {'title': 'मोबाइल फ्रेंडली', 'description': 'हमारे रिस्पॉन्सिव डिज़ाइन के साथ किसी भी डिवाइस से प्लेटफॉर्म तक पहुंचें।'}
        },
        'contact': {
            'title': 'हमसे संपर्क करें',
            'subtitle': 'प्रश्न हैं? हम आपसे सुनना पसंद करेंगे',
            'address': {'title': 'पता', 'value': 'थुडियालुर, कोयंबटूर'},
            'phone': {'title': 'फोन'},
            'email': {'title': 'ईमेल'},
            'form': {'name': 'आपका नाम', 'email': 'आपका ईमेल', 'message': 'आपका संदेश', 'send': 'संदेश भेजें'}
        },
        'footer': {
            'tagline': 'स्वस्थ भविष्य के लिए खेतों को स्कूलों से जोड़ना',
            'quick_links': 'त्वरित लिंक',
            'follow_us': 'हमें फॉलो करें',
            'rights': 'सभी अधिकार सुरक्षित।'
        },
        'login': {
            'title': 'वापस स्वागत है',
            'subtitle': 'अपने Farm2School खाते में लॉगिन करें',
            'email': 'ईमेल पता',
            'password': 'पासवर्ड',
            'remember': 'मुझे याद रखें',
            'forgot': 'पासवर्ड भूल गए?',
            'login_btn': 'लॉगिन',
            'no_account': 'खाता नहीं है?',
            'register_here': 'यहाँ रजिस्टर करें'
        },
        'register': {
            'title': 'खाता बनाएं',
            'subtitle': 'खेतों और स्कूलों को जोड़ने के लिए Farm2School में शामिल हों',
            'user_type': 'मैं हूँ:',
            'farmer': 'किसान',
            'farmer_desc': 'मैं अपनी उपज बेचना चाहता हूँ',
            'school': 'स्कूल',
            'school_desc': 'मैं ताज़ी उपज खरीदना चाहता हूँ',
            'name': 'नाम',
            'email': 'ईमेल पता',
            'district': 'जिला',
            'location': 'विशिष्ट स्थान/पता',
            'password': 'पासवर्ड',
            'register_btn': 'रजिस्टर करें',
            'have_account': 'पहले से खाता है?',
            'login_here': 'यहाँ लॉगिन करें'
        },
        'dashboard': {
            'farmer': {
                'title': 'किसान डैशबोर्ड',
                'schools_in_district': 'आपके जिले में स्कूल',
                'your_products': 'आपके उत्पाद',
                'orders': 'ऑर्डर',
                'add_product': 'उत्पाद जोड़ें',
                'product_name': 'उत्पाद का नाम',
                'description': 'विवरण',
                'price': 'मूल्य (₹)',
                'quantity': 'मात्रा (किलो में)',
                'category': 'श्रेणी',
                'contact': 'संपर्क',
                'delete': 'हटाएं',
                'out_of_stock': 'स्टॉक में नहीं'
            },
            'school': {
                'title': 'स्कूल डैशबोर्ड',
                'farmers_in_district': 'आपके जिले में किसान',
                'available_products': 'उपलब्ध उत्पाद',
                'your_orders': 'आपके ऑर्डर',
                'order': 'ऑर्डर',
                'filter': 'फिल्टर',
                'clear': 'साफ़ करें'
            },
            'common': {
                'home': 'होम',
                'dashboard': 'डैशबोर्ड',
                'messages': 'संदेश',
                'analytics': 'एनालिटिक्स',
                'logout': 'लॉगआउट',
                'products_listed': 'सूचीबद्ध उत्पाद',
                'total_orders': 'कुल ऑर्डर',
                'delivered_orders': 'डिलीवर किए गए ऑर्डर'
            }
        }
    }
}

# Routes
@app.route('/')
def index():
    return render_template('language_select.html')

@app.route('/home')
def home():
    lang = request.args.get('lang', 'en')
    if lang not in translations:
        lang = 'en'
    return render_template('index_multilingual.html', lang=lang, translations=translations[lang])

@app.route('/login', methods=['GET', 'POST'])
def login():
    lang = request.args.get('lang', 'en')
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']
            
            # Debug: Check if form data is received
            print(f"Login attempt - Email: {email}, Password: {'*' * len(password)}")
            
            user = users.find_one({'email': email, 'password': password})
            
            if user:
                session['user_id'] = str(user['_id'])
                session['user_type'] = user['user_type']
                session['lang'] = lang
                
                if user['user_type'] == 'farmer':
                    return redirect(url_for('farmer_dashboard', lang=lang))
                else:
                    return redirect(url_for('school_dashboard', lang=lang))
            else:
                return render_template('login.html', error='Invalid email or password', lang=lang, translations=translations[lang])
                
        except Exception as e:
            print(f"Login error: {str(e)}")
            return render_template('login.html', error=f'Login failed: {str(e)}', lang=lang, translations=translations[lang])
    
    if lang not in translations:
        lang = 'en'
    return render_template('login.html', lang=lang, translations=translations[lang])

@app.route('/register', methods=['GET', 'POST'])
def register():
    lang = request.args.get('lang', 'en')
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        district = request.form['district']
        location = request.form['location']
        
        if users.find_one({'email': email}):
            return render_template('register.html', error='Email already exists', lang=lang, translations=translations[lang])
        
        user_id = users.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'user_type': user_type,
            'district': district,
            'location': location,
            'created_at': datetime.now()
        }).inserted_id
        
        session['user_id'] = str(user_id)
        session['user_type'] = user_type
        session['lang'] = lang
        
        if user_type == 'farmer':
            return redirect(url_for('farmer_dashboard', lang=lang))
        else:
            return redirect(url_for('school_dashboard', lang=lang))
    
    if lang not in translations:
        lang = 'en'
    return render_template('register.html', lang=lang, translations=translations[lang])

@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    lang = request.args.get('lang', session.get('lang', 'en'))
    if lang not in translations:
        lang = 'en'
    session['lang'] = lang
    
    farmer_id = session['user_id']
    user = users.find_one({'_id': ObjectId(farmer_id)})
    farmer_products = list(products.find({'farmer_id': farmer_id}))
    farmer_orders = list(orders.find({'farmer_id': farmer_id}))
    
    # Get nearby schools in same district
    nearby_schools = []
    if user and 'district' in user:
        nearby_schools = list(users.find({
            'user_type': 'school',
            'district': user['district']
        }))
    
    # Enrich orders with product names
    for order in farmer_orders:
        product = products.find_one({'_id': ObjectId(order['product_id'])})
        if product:
            order['product_name'] = product['name']
        else:
            order['product_name'] = "Unknown Product"
    
    return render_template('farmer_dashboard.html', 
                          user=user,
                          products=farmer_products, 
                          orders=farmer_orders,
                          nearby_schools=nearby_schools,
                          lang=lang,
                          translations=translations[lang])

@app.route('/school_dashboard')
def school_dashboard():
    if 'user_id' not in session or session['user_type'] != 'school':
        return redirect(url_for('login'))
    
    lang = request.args.get('lang', session.get('lang', 'en'))
    if lang not in translations:
        lang = 'en'
    session['lang'] = lang
    
    school_id = session['user_id']
    user = users.find_one({'_id': ObjectId(school_id)})
    all_products = list(products.find())
    school_orders = list(orders.find({'school_id': school_id}))
    
    # Get nearby farmers in same district
    nearby_farmers = []
    if user and 'district' in user:
        nearby_farmers = list(users.find({
            'user_type': 'farmer',
            'district': user['district']
        }))
    
    # Enrich orders with product names
    for order in school_orders:
        product = products.find_one({'_id': ObjectId(order['product_id'])})
        if product:
            order['product_name'] = product['name']
        else:
            order['product_name'] = "Unknown Product"
    
    return render_template('school_dashboard.html', 
                          user=user,
                          products=all_products, 
                          orders=school_orders,
                          nearby_farmers=nearby_farmers,
                          lang=lang,
                          translations=translations[lang])

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('messages.html')

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']
        
        try:
            # Store message in database
            contact_message = {
                'name': name,
                'email': email,
                'message': message_text,
                'created_at': datetime.now(),
                'status': 'new'
            }
            messages.insert_one(contact_message)
            
            # Send email to admin
            admin_msg = Message(
                subject=f'New Contact Form Message from {name}',
                recipients=['susmitha.vcsc@gmail.com'],
                body=f'''
                New contact form submission:
                
                Name: {name}
                Email: {email}
                Message: {message_text}
                
                Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                '''
            )
            mail.send(admin_msg)
            
            # Send confirmation email to user
            user_msg = Message(
                subject='Thank you for contacting Farm2School',
                recipients=[email],
                body=f'''
                Dear {name},
                
                Thank you for contacting Farm2School! We have received your message:
                
                "{message_text}"
                
                We will get back to you within 24 hours.
                
                Best regards,
                Farm2School Team
                '''
            )
            mail.send(user_msg)
            
            return redirect(url_for('index') + '?contact=success')
            
        except Exception as e:
            # Still save to database even if email fails
            try:
                contact_message = {
                    'name': name,
                    'email': email,
                    'message': message_text,
                    'created_at': datetime.now(),
                    'status': 'new'
                }
                messages.insert_one(contact_message)
            except:
                pass
            return redirect(url_for('index') + '?contact=error')
    
    return redirect(url_for('index'))

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    quantity = int(request.form['quantity'])
    category = request.form['category']
    
    products.insert_one({
        'farmer_id': session['user_id'],
        'name': name,
        'description': description,
        'price': price,
        'quantity': quantity,
        'category': category,
        'created_at': datetime.now()
    })
    
    return redirect(url_for('farmer_dashboard'))

@app.route('/delete_product', methods=['POST'])
def delete_product():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    product_id = request.form['product_id']
    products.delete_one({'_id': ObjectId(product_id), 'farmer_id': session['user_id']})
    
    return redirect(url_for('farmer_dashboard'))

@app.route('/update_order_status', methods=['POST'])
def update_order_status():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    order_id = request.form['order_id']
    status = request.form['status']
    
    orders.update_one(
        {'_id': ObjectId(order_id), 'farmer_id': session['user_id']},
        {'$set': {'status': status, 'updated_at': datetime.now()}}
    )
    
    return redirect(url_for('farmer_dashboard'))

@app.route('/place_order', methods=['POST'])
def place_order():
    if 'user_id' not in session or session['user_type'] != 'school':
        return redirect(url_for('login'))
    
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    
    product = products.find_one({'_id': ObjectId(product_id)})
    if not product or product['quantity'] < quantity:
        return redirect(url_for('school_dashboard'))
    
    total_price = product['price'] * quantity
    
    orders.insert_one({
        'school_id': session['user_id'],
        'farmer_id': product['farmer_id'],
        'product_id': product_id,
        'quantity': quantity,
        'total_price': total_price,
        'status': 'Pending',
        'created_at': datetime.now()
    })
    
    # Update product quantity
    products.update_one(
        {'_id': ObjectId(product_id)},
        {'$inc': {'quantity': -quantity}}
    )
    
    return redirect(url_for('school_dashboard'))

@app.route('/contact_farmer/<farmer_id>')
def contact_farmer(farmer_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    farmer = users.find_one({'_id': ObjectId(farmer_id), 'user_type': 'farmer'})
    if not farmer:
        return redirect(url_for('school_dashboard'))
    
    # Get farmer's products
    farmer_products = list(products.find({'farmer_id': farmer_id}))
    
    return render_template('contact_farmer.html', farmer=farmer, products=farmer_products)

@app.route('/send_message', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    farmer_id = request.form['farmer_id']
    message = request.form['message']
    sender_name = request.form['sender_name']
    sender_email = request.form['sender_email']
    
    # Here you would typically save the message to database or send email
    # For now, we'll just redirect back with a success message
    
    return redirect(url_for('contact_farmer', farmer_id=farmer_id) + '?sent=1')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)