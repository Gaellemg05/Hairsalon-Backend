RESPONSES = {
    "hello": "Hello! I'm LuxeSalon's hair care assistant. Ask me about hairstyles, hair treatments, or trends!",
    "hi": "Hi! How can I help you with your hair today?",
    "thanks": "You're welcome! Feel free to ask if you have more questions.",
    "bye": "Goodbye and take care of your hair!",
}

HAIR_TYPES = {
    "kinky": "For kinky/coily hair (type 4), hydration is essential. Use a daily leave-in conditioner, prioritize protective styles (braids, twists), wash with a gentle shampoo 1x/week, and sleep with a satin bonnet. Shea butter and coconut oil are your best friends.",
    "curly": "Curly hair (type 3) needs definition and moisture. Use the LOC method (Liquid-Oil-Cream), a mousse or gel to define curls, and trim every 2-3 months. A diffuser attachment helps achieve bouncy curls.",
    "straight": "Straight hair gets oily faster. Wash 2-3x per week max, use dry shampoo between washes, and always apply heat protectant before using hot tools. A texturizing spray can add volume and movement.",
    "afro": "Afro-textured hair (type 4) is beautiful! Deep condition 1x/week, wear protective styles (braids, twists, locs), detangle with a wide-tooth comb on wet hair, and use castor oil for growth.",
}

STYLES = {
    "braids": "Several braid types are available: Box braids (individual, 4-8 weeks), Cornrows (scalp braids), Ghana braids (thick with extensions), Knotless (no knot, lighter). Price: 15,000 - 40,000 FCFA depending on length and complexity.",
    "locs": "Dreadlocks can be natural (freeform), fine (sisterlocks), or temporary (faux locs). Maintenance includes washing every 1-2 weeks and retwisting every 4-6 weeks. Price: 20,000 - 60,000 FCFA for installation.",
    "twists": "Twists are elegant and protective. Two-strand twists, Senegalese twists (fine with extensions), or Havana twists (thick and voluminous). Duration: 4-6 weeks. Price: 20,000 - 50,000 FCFA.",
    "weave": "Weave/extensions let you change your look instantly. Sew-in (stitched on braids), wig (versatile), or fusion (glued). Always use a professional. Price: 30,000 - 80,000 FCFA including installation.",
    "relaxer": "A relaxer is a permanent chemical straightener. Brazilian keratin smoothing is semi-permanent. Botox treatment is formaldehyde-free. Space relaxers 8-12 weeks apart to protect your hair.",
}

CONCERNS = {
    "hair loss": "Hair loss can be caused by stress, nutritional deficiencies, hormones, or tight hairstyles. Solutions: castor oil scalp massage 3x/week, iron-rich diet (spinach, eggs, avocado), avoid tight styles. See a dermatologist if it persists.",
    "dandruff": "There are dry dandruff (small white flakes) or oily (yellowish). Use an anti-dandruff shampoo with salicylic acid or zinc, rinse with diluted apple cider vinegar 1x/week, and massage with tea tree oil. Avoid harsh shampoos.",
    "dry": "Dry hair lacks moisture. Follow this routine: 1) Sulfate-free gentle shampoo, 2) Hydrating conditioner, 3) Leave-in conditioner, 4) Sealing oil (coconut, jojoba, shea). The LOC method locks in moisture longer.",
    "breakage": "Breakage means your hair lacks protein or moisture. Do an egg and yogurt mask 1x/week, apply pure shea butter after washing, reduce heat, and protect ends with a light oil. Avoid rubber bands, use satin scrunchies instead.",
    "short": "Short hair is trendy! Style ideas: Pixie cut (very short, easy), Bob (elegant and timeless), TWA (Teeny Weeny Afro). Benefits: easy to style, less product needed, modern and fresh look.",
}

EVENTS = {
    "wedding": "For a wedding, choose an elegant updo with accessories (pearls, flowers), braids adorned with jewelry, twists with added hair for volume, or a smooth style with soft curls. Budget: 30,000 - 100,000 FCFA. Do a trial 1 month before.",
    "party": "For a party or evening out: high bun with jewelry, geometric cornrow patterns, sleek straight with highlights, or half-up half-down with curls. Add accessories (barrettes, pearls, chains) for glamour.",
    "office": "For the office, keep it polished: low classic bun, discreet cornrows, short twists, or well-moisturized natural afro. Choose a style that lasts at least a week.",
}

RECOMMENDATIONS = {
    "hot": "For hot weather, choose light braids or twists, high buns, natural afro, or bantu knots. Use a rose water spray to refresh your hair throughout the day.",
    "rainy": "For rainy season, go with cornrows, twists, low buns, or a protective headwrap. A satin shower cap protects your style on rainy days.",
}

PRODUCTS = {
    "natural": "Essential natural products: shea butter (intense moisture), coconut oil (penetrates the hair shaft), castor oil (stimulates growth), aloe vera (soothes and hydrates), honey (natural humectant), apple cider vinegar (balances pH).",
    "brands": "Available brands in Cameroon: SheaMoisture (moisture), Mielle Organics (textured hair), ORS (creamy treatments), Dark & Lovely (color and relaxers), Afro Love (local Cameroonian brand), Kemi Oyl (premium natural oils).",
}

SALON_TIPS = {
    "choose": "When choosing a salon, check: cleanliness and hygiene, portfolio of work, client reviews, transparent pricing, and products used. On LuxeSalon, you can read reviews and book directly.",
    "prices": "Indicative prices in Cameroon: Box braids 15,000-40,000 FCFA, Twists 20,000-50,000 FCFA, Relaxer 10,000-25,000 FCFA, Cut & blow-dry 5,000-15,000 FCFA, Deep treatment 7,000-15,000 FCFA, Wig installation 30,000-80,000 FCFA. Prices vary by length and complexity.",
}

GENERAL_ADVICE = (
    "Hydrate your hair regularly, protect it at night with a satin bonnet, "
    "avoid excessive heat, get regular trims, and use products suited to your hair type."
)


def match_any(text, words):
    text_lower = text.lower()
    for w in words:
        if w in text_lower:
            return True
    return False


def get_response(message):
    msg = message.strip().lower()

    if not msg:
        return RESPONSES["hello"]

    # Short greetings
    if len(msg.split()) <= 3:
        for greeting, response in RESPONSES.items():
            if msg == greeting or msg.startswith(greeting):
                return response

    # Hair types
    if match_any(msg, ["kinky", "coily", "type 4", "4a", "4b", "4c", "natural hair"]):
        return HAIR_TYPES["kinky"]
    if match_any(msg, ["curly", "wavy", "type 3", "loop", "curl"]):
        return HAIR_TYPES["curly"]
    if match_any(msg, ["straight", "type 1", "type 2", "sleek"]):
        return HAIR_TYPES["straight"]
    if match_any(msg, ["afro", "natural", "african"]):
        return HAIR_TYPES["afro"]

    # Concerns
    if match_any(msg, ["hair loss", "losing hair", "falling out", "balding", "thinning"]):
        return CONCERNS["hair loss"]
    if match_any(msg, ["dandruff", "itchy", "flakes", "scalp"]):
        return CONCERNS["dandruff"]
    if match_any(msg, ["dry hair", "dryness", "dehydrated", "lacks moisture"]):
        return CONCERNS["dry"]
    if match_any(msg, ["breakage", "split ends", "snapping", "breaking", "damage"]):
        return CONCERNS["breakage"]
    if match_any(msg, ["short hair", "grow", "growth", "length", "pixie", "bob"]):
        return CONCERNS["short"]

    # Styles
    if match_any(msg, ["braid", "box braid", "cornrow", "ghana", "knotless"]):
        return STYLES["braids"]
    if match_any(msg, ["dread", "lock", "sisterlock", "faux loc", "loc"]):
        return STYLES["locs"]
    if match_any(msg, ["twist", "senegalese", "havana", "kinky twist"]):
        return STYLES["twists"]
    if match_any(msg, ["weave", "sew-in", "extension", "wig", "fusion", "sew in"]):
        return STYLES["weave"]
    if match_any(msg, ["relaxer", "straighten", "smooth", "keratin", "brazilian", "perm"]):
        return STYLES["relaxer"]

    # Events
    if match_any(msg, ["wedding", "bride", "bridal"]):
        return EVENTS["wedding"]
    if match_any(msg, ["party", "evening", "night out", "gala", "prom"]):
        return EVENTS["party"]
    if match_any(msg, ["office", "work", "professional", "job interview"]):
        return EVENTS["office"]

    # Seasonal
    if match_any(msg, ["hot", "sun", "summer", "heat"]):
        return RECOMMENDATIONS["hot"]
    if match_any(msg, ["rain", "rainy", "humid", "season", "winter"]):
        return RECOMMENDATIONS["rainy"]

    # Products
    if match_any(msg, ["natural product", "shea butter", "coconut oil", "castor oil", "aloe vera"]):
        return PRODUCTS["natural"]
    if match_any(msg, ["brand", "buy", "sheamoisture", "mielle", "afro love", "product"]):
        return PRODUCTS["brands"]

    # Salon
    if match_any(msg, ["choose a salon", "good salon", "find a salon", "best salon"]):
        return SALON_TIPS["choose"]
    if match_any(msg, ["price", "cost", "how much", "expensive", "cheap", "fee"]):
        return SALON_TIPS["prices"]

    # General advice
    if match_any(msg, ["advice", "recommend", "tip", "how to", "idea", "suggestion"]):
        return f"Here are some general tips: {GENERAL_ADVICE}\n\nTell me your hair type or what you're looking for and I'll give more specific advice."

    # Greeting in longer messages
    if match_any(msg, ["hello", "hi", "hey"]):
        return RESPONSES["hi"] + "\n\n" + GENERAL_ADVICE + "\n\nWhat hair information are you looking for?"

    if match_any(msg, ["thanks", "thank"]):
        return RESPONSES["thanks"]

    import random
    fallbacks = [
        "I didn't quite understand your question. Try asking about hair types (kinky, curly, afro), styles (braids, twists, locs), or concerns (hair loss, dryness, dandruff).",
        "Could you rephrase that? I can help with hair types, hairstyles, treatments, or product recommendations.",
        "Sorry, I don't have a specific answer for that. Try: tips for curly hair, wedding hairstyle ideas, or how to treat dry hair.",
    ]
    return random.choice(fallbacks)
