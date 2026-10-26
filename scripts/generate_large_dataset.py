"""
=============================================================
Large E-Commerce Dataset Generator
=============================================================
Generates synthetic but realistic e-commerce interaction data
for Big Data demonstration with Apache Spark.

Supports generation of 100K to 1M+ records.
=============================================================
"""

import csv
import random
import os
import sys
import time
import argparse
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
random.seed(42)

# ─────────────────────────────────────────────
# PRODUCT CATALOGUE  (realistic product names)
# ─────────────────────────────────────────────
PRODUCT_CATALOGUE = {
    "Electronics": [
        ("Lenovo IdeaPad 5 Laptop", 45999),
        ("Dell Inspiron 15 3000", 52999),
        ("HP Pavilion x360", 61999),
        ("Acer Aspire 7 Gaming Laptop", 72999),
        ("Apple MacBook Air M2", 114990),
        ("Samsung Galaxy S23 Ultra", 124999),
        ("OnePlus 12R 5G", 42999),
        ("Xiaomi 14", 69999),
        ("Realme GT 5G", 29999),
        ("Apple iPhone 15", 79900),
        ("Sony WH-1000XM5 Headphones", 26990),
        ("JBL Tune 510BT", 3499),
        ("boAt Airdopes 141", 1299),
        ("Samsung 65-inch QLED TV", 109990),
        ("LG 43-inch 4K TV", 44990),
        ("Sony Bravia 55-inch", 82990),
        ("Logitech MX Master 3 Mouse", 8495),
        ("Razer DeathAdder V3 Mouse", 6999),
        ("Mechanical Gaming Keyboard", 4999),
        ("Dell 27-inch Monitor IPS", 22999),
        ("LG 24-inch UltraWide Monitor", 18490),
        ("Seagate 2TB External HDD", 4599),
        ("WD 1TB SSD External", 7999),
        ("Samsung 970 EVO 500GB NVMe", 5999),
        ("D-Link WiFi 6 Router", 8999),
        ("Netgear Nighthawk AX12", 22999),
        ("Anker 65W GaN Charger", 2499),
        ("Belkin USB-C Hub 7-in-1", 3999),
        ("GoPro Hero 12 Black", 36000),
        ("Canon EOS 1500D DSLR Camera", 32999),
    ],
    "Fashion": [
        ("Levi's 511 Slim Fit Jeans", 2999),
        ("Allen Solly Formal Shirt", 1599),
        ("Nike Air Max 270 Sneakers", 9995),
        ("Adidas Ultraboost 23", 14999),
        ("Puma Running Shoes", 4499),
        ("H&M Basic Cotton T-Shirt", 799),
        ("Zara Slim Chino Trousers", 3490),
        ("Reebok Classic Sneakers", 5999),
        ("Peter England Formal Blazer", 5999),
        ("Van Heusen Polo T-Shirt", 1299),
        ("Arrow Checked Shirt", 2199),
        ("Woodland Trekking Shoes", 4999),
        ("Bata Leather Formal Shoes", 3499),
        ("Roadster Cargo Pants", 1499),
        ("Wrangler Regular Fit Jeans", 2199),
        ("Lee Denim Jacket", 3999),
        ("Tommy Hilfiger Cap", 1499),
        ("Ray-Ban Aviator Sunglasses", 7290),
        ("Fossil Chronograph Watch", 12995),
        ("Titan Raga Women's Watch", 8995),
    ],
    "Home & Kitchen": [
        ("Prestige Induction Cooktop", 2499),
        ("Bajaj Mixer Grinder 750W", 1999),
        ("Philips Air Fryer XXL", 8999),
        ("Havells Espresso Coffee Maker", 3499),
        ("Morphy Richards Pop-up Toaster", 1499),
        ("Inalsa Hand Blender", 1299),
        ("Milton Hot-Cold Water Bottle", 599),
        ("Cello Plastic Containers Set", 799),
        ("Amazon Basics Bedsheet Set", 1299),
        ("Bombay Dyeing Pillow Set", 899),
        ("IKEA Billy Bookshelf", 7990),
        ("Nilkamal Plastic Chair", 1499),
        ("Solimo Wardrobe Organiser", 599),
        ("WD-40 Multi-Use Lubricant", 399),
        ("Scotch-Brite Scrub Pad Pack", 199),
        ("Godrej Aer Air Freshener", 299),
        ("Pigeon Non-Stick Cookware Set", 2499),
        ("Wonderchef Granite Frypan", 1799),
        ("Asian Paints Smart Care", 599),
        ("Luminous 150Ah Battery", 12500),
    ],
    "Books": [
        ("Clean Code by Robert Martin", 599),
        ("The Pragmatic Programmer", 799),
        ("Atomic Habits by James Clear", 499),
        ("Deep Work by Cal Newport", 449),
        ("Python Crash Course", 699),
        ("Data Science Handbook", 999),
        ("Machine Learning with Python", 799),
        ("The Alchemist by Paulo Coelho", 299),
        ("Ikigai: Japanese Secret", 399),
        ("Rich Dad Poor Dad", 349),
        ("Zero to One by Peter Thiel", 499),
        ("Sapiens by Yuval Noah Harari", 549),
        ("The Lean Startup", 449),
        ("Thinking Fast and Slow", 599),
        ("12 Rules for Life", 499),
    ],
    "Sports": [
        ("Yonex ZR100 Badminton Racket", 1299),
        ("Cosco Cricket Bat", 1999),
        ("Nivia Football Size 5", 799),
        ("Decathlon Yoga Mat 8mm", 999),
        ("Powerfit Resistance Bands Set", 599),
        ("Strauss Gym Gloves", 499),
        ("Whey Protein 2kg Chocolate", 2499),
        ("MuscleBlaze BCAA 250g", 799),
        ("Healthkart Creatine 250g", 599),
        ("Adidas Running Track Pants", 2499),
        ("Nivia Basketball", 899),
        ("Cosco Table Tennis Set", 1499),
        ("Italtrike Cycle 26-inch", 8999),
        ("Boldfit Skipping Rope", 399),
        ("Strauss Foam Roller", 699),
    ],
    "Beauty": [
        ("L'Oreal Paris Serum", 799),
        ("Nivea Men Face Wash", 199),
        ("Lakme Absolute Foundation", 599),
        ("Himalaya Neem Face Wash", 149),
        ("Biotique Bio Papaya Scrub", 299),
        ("Dove Body Lotion 400ml", 349),
        ("Park Avenue Deo Spray", 249),
        ("Mamaearth Vitamin C Serum", 599),
        ("The Ordinary Niacinamide 10%", 699),
        ("Plum Green Tea Toner", 449),
        ("Minimalist 2% Salicylic Acid", 499),
        ("Beardo Beard Growth Oil", 399),
        ("WOW Skin Science Shampoo", 449),
        ("OGX Argan Oil Conditioner", 749),
        ("Colorbar Cosmetics Lipstick", 549),
    ],
    "Grocery": [
        ("Tata Tea Gold 500g", 299),
        ("Nescafe Classic Coffee 200g", 499),
        ("Maggi Noodles 12-Pack", 149),
        ("Amul Butter 500g", 279),
        ("Fortune Sunflower Oil 5L", 699),
        ("Aashirvaad Atta 10kg", 499),
        ("Saffola Oats 1kg", 299),
        ("Borges Olive Oil 500ml", 599),
        ("Himalayan Pink Salt 1kg", 199),
        ("Organic India Tulsi Tea", 299),
        ("Patanjali Desi Ghee 1kg", 699),
        ("Dabur Honey 1kg", 499),
        ("Haldirams Bhujia 400g", 199),
        ("Bikaji Aloo Bhujia", 149),
        ("Cadbury Dairy Milk 160g", 99),
    ],
    "Toys": [
        ("LEGO Classic Bricks 484pcs", 3499),
        ("Hot Wheels 20-Car Gift Set", 1299),
        ("Barbie Dreamhouse", 5999),
        ("Funskool Cricket Set Junior", 899),
        ("Play-Doh Mega Fun Factory", 1499),
        ("Nerf Elite Blaster", 1999),
        ("Milton Toys Car Racing Track", 1299),
        ("Funskool Candy Land Board Game", 799),
        ("Rubik's Cube 3x3", 449),
        ("Remote Control Car 1:16 Scale", 1999),
        ("Kids Drawing Board Magnetic", 699),
        ("Baby Musical Piano Toy", 899),
        ("Funskool Chess Set", 599),
        ("Masha and the Bear Doll Set", 1299),
        ("LOL Surprise OMG Doll", 2499),
    ],
}

# Flatten to list: [(product_id, name, category, price), ...]
ALL_PRODUCTS = []
pid = 1001
for category, products in PRODUCT_CATALOGUE.items():
    for name, price in products:
        ALL_PRODUCTS.append({
            "product_id": pid,
            "product_name": name,
            "category": category,
            "price": price,
        })
        pid += 1

TOTAL_PRODUCTS = len(ALL_PRODUCTS)

# Interaction types and scores
INTERACTION_TYPES = {
    "view": 1,
    "click": 2,
    "wishlist": 2,
    "add_to_cart": 3,
    "purchase": 5,
}

# Category preference weights per user type
USER_TYPES = {
    "tech_enthusiast": {"Electronics": 0.5, "Books": 0.2, "Sports": 0.1, "Fashion": 0.1, "Home & Kitchen": 0.1},
    "fashionista": {"Fashion": 0.5, "Beauty": 0.3, "Home & Kitchen": 0.1, "Grocery": 0.05, "Toys": 0.05},
    "home_maker": {"Home & Kitchen": 0.4, "Grocery": 0.3, "Beauty": 0.15, "Toys": 0.1, "Books": 0.05},
    "fitness_lover": {"Sports": 0.5, "Grocery": 0.2, "Electronics": 0.15, "Fashion": 0.1, "Books": 0.05},
    "bookworm": {"Books": 0.5, "Electronics": 0.2, "Home & Kitchen": 0.15, "Grocery": 0.1, "Sports": 0.05},
    "parent": {"Toys": 0.35, "Home & Kitchen": 0.25, "Grocery": 0.2, "Fashion": 0.1, "Books": 0.1},
    "general": {cat: 1/len(PRODUCT_CATALOGUE) for cat in PRODUCT_CATALOGUE},
}


def get_products_by_category(category: str):
    return [p for p in ALL_PRODUCTS if p["category"] == category]


def weighted_category_choice(user_type: str) -> str:
    weights = USER_TYPES[user_type]
    categories = list(weights.keys())
    probs = list(weights.values())
    return random.choices(categories, weights=probs, k=1)[0]


def generate_rating(interaction_type: str) -> float:
    """Generate a realistic rating based on interaction type."""
    if interaction_type in ("purchase", "add_to_cart"):
        # Generally happy buyers
        return round(random.choices(
            [1.0, 2.0, 3.0, 4.0, 5.0],
            weights=[0.02, 0.05, 0.13, 0.40, 0.40]
        )[0], 1)
    elif interaction_type == "view":
        return round(random.uniform(1.0, 5.0), 1)
    else:
        return round(random.choices(
            [1.0, 2.0, 3.0, 4.0, 5.0],
            weights=[0.03, 0.07, 0.20, 0.35, 0.35]
        )[0], 1)


def random_timestamp(start_days_ago=365, end_days_ago=0):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() - timedelta(days=end_days_ago)
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def generate_review(product_name: str, rating: float) -> str:
    """Generate a simple review based on rating."""
    positive = [
        f"Great product! Highly recommend {product_name}.",
        f"Excellent quality, very satisfied with {product_name}.",
        f"Best purchase I made. {product_name} is amazing.",
        f"Worth every rupee! {product_name} works perfectly.",
        f"Outstanding product. {product_name} exceeded expectations.",
    ]
    neutral = [
        f"Decent product. {product_name} is okay for the price.",
        f"Average quality. {product_name} works as described.",
        f"Nothing special but {product_name} gets the job done.",
        f"Value for money. {product_name} is acceptable.",
    ]
    negative = [
        f"Disappointed with {product_name}. Not as described.",
        f"Poor quality. {product_name} broke within a week.",
        f"Not worth the price. {product_name} was a waste.",
        f"Would not recommend {product_name}.",
    ]
    if rating >= 4.0:
        return random.choice(positive)
    elif rating >= 2.5:
        return random.choice(neutral)
    else:
        return random.choice(negative)


def generate_dataset(
    num_users: int = 5000,
    num_interactions: int = 100_000,
    output_path: str = "data/raw/ecommerce_interactions.csv",
    chunk_size: int = 10_000,
    verbose: bool = True,
):
    """
    Generate the base e-commerce dataset.

    Args:
        num_users       : Number of unique users to simulate
        num_interactions: Total interaction records to generate
        output_path     : CSV output file path
        chunk_size      : Write records in chunks to avoid RAM usage
        verbose         : Print progress
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if verbose:
        print(f"[INFO] Generating dataset: {num_interactions:,} records")
        print(f"[INFO] Users: {num_users:,}  |  Products: {TOTAL_PRODUCTS}")
        print(f"[INFO] Output: {output_path}")

    # Pre-assign user types
    user_types = {
        uid: random.choice(list(USER_TYPES.keys()))
        for uid in range(1001, 1001 + num_users)
    }

    start_time = time.time()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "interaction_id", "user_id", "user_name", "user_email",
            "product_id", "product_name", "category", "price",
            "interaction_type", "interaction_score", "rating",
            "review", "timestamp"
        ])

        interaction_id = 1
        batch = []

        for _ in range(num_interactions):
            user_id = random.randint(1001, 1000 + num_users)
            user_type = user_types[user_id]

            # Choose category based on user preference
            cat = weighted_category_choice(user_type)
            cat_products = get_products_by_category(cat)
            if not cat_products:
                cat_products = ALL_PRODUCTS

            product = random.choice(cat_products)
            interaction_type = random.choices(
                list(INTERACTION_TYPES.keys()),
                weights=[0.40, 0.20, 0.15, 0.15, 0.10],
                k=1
            )[0]
            interaction_score = INTERACTION_TYPES[interaction_type]
            rating = generate_rating(interaction_type)
            review = ""
            if interaction_type in ("purchase", "add_to_cart") and random.random() < 0.4:
                review = generate_review(product["product_name"], rating)

            ts = random_timestamp()

            batch.append([
                interaction_id,
                user_id,
                fake.name(),
                f"user{user_id}@example.com",
                product["product_id"],
                product["product_name"],
                product["category"],
                product["price"],
                interaction_type,
                interaction_score,
                rating,
                review,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
            ])

            interaction_id += 1

            if len(batch) >= chunk_size:
                writer.writerows(batch)
                batch.clear()
                if verbose:
                    pct = (interaction_id / num_interactions) * 100
                    elapsed = time.time() - start_time
                    rate = interaction_id / elapsed if elapsed > 0 else 0
                    print(f"\r  Progress: {interaction_id:>10,}/{num_interactions:,} "
                          f"({pct:5.1f}%)  Rate: {rate:,.0f} rec/s", end="", flush=True)

        if batch:
            writer.writerows(batch)

    elapsed = time.time() - start_time
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if verbose:
        print(f"\n[DONE] Generated {num_interactions:,} records in {elapsed:.1f}s")
        print(f"[INFO] File size: {size_mb:.1f} MB  |  Path: {output_path}")

    return output_path


def generate_large_dataset(
    output_path: str = "data/raw/ecommerce_large.csv",
    target_records: int = 1_000_000,
    num_users: int = 50_000,
):
    """
    Generate a LARGE dataset (1M+ records) for Big Data demonstration.
    Uses streaming write to avoid memory issues.
    """
    print("=" * 60)
    print("  BIG DATA DATASET GENERATOR")
    print(f"  Target: {target_records:,} interaction records")
    print(f"  Users : {num_users:,}")
    print(f"  Output: {output_path}")
    print("=" * 60)

    generate_dataset(
        num_users=num_users,
        num_interactions=target_records,
        output_path=output_path,
        chunk_size=50_000,
        verbose=True,
    )


def generate_products_csv(output_path: str = "data/raw/products.csv"):
    """Save the product catalogue to CSV."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["product_id", "product_name", "category", "price"])
        writer.writeheader()
        writer.writerows(ALL_PRODUCTS)
    print(f"[INFO] Products CSV saved: {output_path} ({len(ALL_PRODUCTS)} products)")
    return ALL_PRODUCTS


# ────────────────────────────────────────────────────────────
# CLI entry point
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="E-Commerce Dataset Generator for Big Data Spark Project"
    )
    parser.add_argument(
        "--mode",
        choices=["small", "large", "both"],
        default="small",
        help="Generate small (100K), large (1M), or both datasets",
    )
    parser.add_argument(
        "--users",
        type=int,
        default=5000,
        help="Number of unique users for small dataset (default: 5000)",
    )
    parser.add_argument(
        "--records",
        type=int,
        default=100_000,
        help="Number of interaction records for small dataset (default: 100000)",
    )
    parser.add_argument(
        "--large-users",
        type=int,
        default=50_000,
        help="Number of unique users for large dataset (default: 50000)",
    )
    parser.add_argument(
        "--large-records",
        type=int,
        default=1_000_000,
        help="Number of records for large dataset (default: 1000000)",
    )
    args = parser.parse_args()

    print("\n[INFO] E-Commerce Spark Recommendation -- Dataset Generator\n")

    # Always generate product catalogue
    generate_products_csv()

    if args.mode in ("small", "both"):
        print(f"\n[INFO] Generating SMALL dataset ({args.records:,} records)...")
        generate_dataset(
            num_users=args.users,
            num_interactions=args.records,
            output_path="data/raw/ecommerce_interactions.csv",
            verbose=True,
        )

    if args.mode in ("large", "both"):
        print(f"\n[INFO] Generating LARGE dataset ({args.large_records:,} records)...")
        generate_large_dataset(
            output_path="data/raw/ecommerce_large.csv",
            target_records=args.large_records,
            num_users=args.large_users,
        )

    print("\n[SUCCESS] Dataset generation complete!")
