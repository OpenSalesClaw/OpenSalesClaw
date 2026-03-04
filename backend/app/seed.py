"""Application seeding module.

Two distinct operations are provided:

* ``ensure_default_user`` — always runs at startup. Creates the admin user
  defined by ``settings.default_admin_email`` / ``settings.default_admin_password``
  if one does not already exist. Idempotent.

* ``seed_demo_data`` — runs only when ``settings.seed_demo_data`` is ``True``.
  Populates ~20 accounts, ~50 contacts, and ~30 leads with realistic CRM data.
  Idempotent: checks for a sentinel account before inserting.
"""

import logging
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models.account import Account
from app.models.case import Case
from app.models.contact import Contact
from app.models.lead import Lead
from app.models.opportunity import Opportunity
from app.models.role import Role
from app.models.user import User
from app.services.case import _generate_case_number

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Sentinel value used to detect existing demo data
# ---------------------------------------------------------------------------

_SENTINEL_ACCOUNT = "Acme Corporation"


# ---------------------------------------------------------------------------
# Default admin user
# ---------------------------------------------------------------------------


async def ensure_default_user(db: AsyncSession) -> User:
    """Create the default admin user if it does not already exist.

    Returns the existing or newly-created ``User`` instance.
    """
    result = await db.execute(
        select(User).where(User.email == settings.default_admin_email, User.is_deleted.is_(False))
    )
    user = result.scalars().first()

    if user is not None:
        logger.info("Default admin user already exists — skipping creation (%s)", settings.default_admin_email)
        return user

    user = User(
        email=settings.default_admin_email,
        hashed_password=hash_password(settings.default_admin_password),
        first_name="Admin",
        last_name="User",
        is_active=True,
        is_superuser=True,
    )
    db.add(user)
    await db.flush()
    # Set self-referential audit columns after we know the ID.
    user.created_by_id = user.id
    user.updated_by_id = user.id
    user.owner_id = user.id
    await db.flush()
    await db.refresh(user)
    logger.info("Default admin user created: %s", settings.default_admin_email)
    return user


# ---------------------------------------------------------------------------
# Demo data definitions
# ---------------------------------------------------------------------------


@dataclass
class _AccountData:
    name: str
    type: str
    industry: str
    website: str
    phone: str
    billing_city: str
    billing_country: str
    annual_revenue: float
    number_of_employees: int
    description: str = ""


@dataclass
class _ContactData:
    account_name: str  # references _AccountData.name
    first_name: str
    last_name: str
    email: str
    title: str
    department: str
    phone: str


@dataclass
class _LeadData:
    first_name: str
    last_name: str
    company: str
    email: str
    phone: str
    title: str
    status: str
    lead_source: str
    industry: str


@dataclass
class _RoleData:
    name: str
    description: str


@dataclass
class _OpportunityData:
    name: str
    account_name: str
    stage: str
    amount: float
    close_date: str  # ISO date string YYYY-MM-DD


@dataclass
class _CaseData:
    subject: str
    account_name: str
    description: str
    status: str
    priority: str
    origin: str


_ACCOUNTS: list[_AccountData] = [
    _AccountData(
        "Acme Corporation",
        "Customer",
        "Manufacturing",
        "https://acme.example.com",
        "+1-555-100-0001",
        "San Francisco",
        "United States",
        12_500_000,
        450,
        "Long-standing enterprise customer.",
    ),
    _AccountData(
        "Globex Industries",
        "Partner",
        "Energy",
        "https://globex.example.com",
        "+1-555-100-0002",
        "Houston",
        "United States",
        87_000_000,
        1_200,
        "Strategic partner in the energy sector.",
    ),
    _AccountData(
        "Stark Enterprises",
        "Customer",
        "Technology",
        "https://stark.example.com",
        "+1-555-100-0003",
        "New York",
        "United States",
        340_000_000,
        5_000,
        "Enterprise tech conglomerate.",
    ),
    _AccountData(
        "Wayne Industries",
        "Customer",
        "Defense",
        "https://wayne.example.com",
        "+1-555-100-0004",
        "Gotham",
        "United States",
        215_000_000,
        3_400,
        "Defense and research corporation.",
    ),
    _AccountData(
        "Umbrella Corp",
        "Prospect",
        "Pharmaceuticals",
        "https://umbrella.example.com",
        "+44-20-7946-0001",
        "London",
        "United Kingdom",
        9_000_000,
        300,
        "Pharmaceutical company under evaluation.",
    ),
    _AccountData(
        "Initech Solutions",
        "Customer",
        "Technology",
        "https://initech.example.com",
        "+1-555-100-0006",
        "Austin",
        "United States",
        6_300_000,
        120,
        "Mid-market software services firm.",
    ),
    _AccountData(
        "Weyland-Yutani",
        "Partner",
        "Space Technology",
        "https://weyland.example.com",
        "+1-555-100-0007",
        "Los Angeles",
        "United States",
        780_000_000,
        12_000,
        "Aerospace and robotics joint partner.",
    ),
    _AccountData(
        "Pied Piper",
        "Customer",
        "Technology",
        "https://piedpiper.example.com",
        "+1-555-100-0008",
        "Palo Alto",
        "United States",
        4_200_000,
        45,
        "Compression algorithm startup.",
    ),
    _AccountData(
        "Hooli",
        "Prospect",
        "Technology",
        "https://hooli.example.com",
        "+1-555-100-0009",
        "San Francisco",
        "United States",
        520_000_000,
        8_000,
        "Large tech company; potential enterprise deal.",
    ),
    _AccountData(
        "Dunder Mifflin",
        "Customer",
        "Retail",
        "https://dundermifflin.example.com",
        "+1-555-100-0010",
        "Scranton",
        "United States",
        2_100_000,
        80,
        "Paper and office supply company.",
    ),
    _AccountData(
        "Buy n Large",
        "Customer",
        "Retail",
        "https://buynlarge.example.com",
        "+1-555-100-0011",
        "Chicago",
        "United States",
        400_000_000,
        6_500,
        "Mega-retailer and services provider.",
    ),
    _AccountData(
        "Soylent Corp",
        "Prospect",
        "Food & Beverage",
        "https://soylent.example.com",
        "+1-555-100-0012",
        "Seattle",
        "United States",
        3_800_000,
        90,
        "Alternative food products company.",
    ),
    _AccountData(
        "Oscorp",
        "Customer",
        "Biotechnology",
        "https://oscorp.example.com",
        "+1-555-100-0013",
        "New York",
        "United States",
        98_000_000,
        1_800,
        "Biotechnology and genetics research firm.",
    ),
    _AccountData(
        "LexCorp",
        "Partner",
        "Energy",
        "https://lexcorp.example.com",
        "+1-555-100-0014",
        "Metropolis",
        "United States",
        167_000_000,
        2_700,
        "Energy and tech diversified partner.",
    ),
    _AccountData(
        "Capsule Corporation",
        "Customer",
        "Automotive",
        "https://capsule.example.com",
        "+81-3-0000-0001",
        "Tokyo",
        "Japan",
        230_000_000,
        4_100,
        "Automotive and capsule technology leader.",
    ),
    _AccountData(
        "Cyberdyne Systems",
        "Prospect",
        "Technology",
        "https://cyberdyne.example.com",
        "+1-555-100-0016",
        "Sunnyvale",
        "United States",
        45_000_000,
        600,
        "AI and robotics R&D company.",
    ),
    _AccountData(
        "Tyrell Corporation",
        "Customer",
        "Biotechnology",
        "https://tyrell.example.com",
        "+1-555-100-0017",
        "Los Angeles",
        "United States",
        310_000_000,
        4_500,
        "Advanced biotech and replicant manufacturer.",
    ),
    _AccountData(
        "Momcorp",
        "Vendor",
        "Robotics",
        "https://momcorp.example.com",
        "+1-555-100-0018",
        "New New York",
        "United States",
        890_000_000,
        14_000,
        "Dominant robot manufacturer and supplier.",
    ),
    _AccountData(
        "Rekall",
        "Prospect",
        "Travel",
        "https://rekall.example.com",
        "+1-555-100-0019",
        "Denver",
        "United States",
        1_200_000,
        30,
        "Virtual reality travel startup.",
    ),
    _AccountData(
        "Vandelay Industries",
        "Customer",
        "Import/Export",
        "https://vandelay.example.com",
        "+1-555-100-0020",
        "New York",
        "United States",
        8_700_000,
        150,
        "Import/export trading company.",
    ),
]

_CONTACTS: list[_ContactData] = [
    # Acme Corporation (5)
    _ContactData(
        "Acme Corporation",
        "Carol",
        "Reynolds",
        "carol.reynolds@acme.example.com",
        "VP of Engineering",
        "Engineering",
        "+1-555-201-0001",
    ),
    _ContactData(
        "Acme Corporation",
        "James",
        "Holden",
        "james.holden@acme.example.com",
        "Account Executive",
        "Sales",
        "+1-555-201-0002",
    ),
    _ContactData(
        "Acme Corporation",
        "Naomi",
        "Nagata",
        "naomi.nagata@acme.example.com",
        "Lead Engineer",
        "Engineering",
        "+1-555-201-0003",
    ),
    _ContactData(
        "Acme Corporation",
        "Amos",
        "Burton",
        "amos.burton@acme.example.com",
        "Field Technician",
        "Operations",
        "+1-555-201-0004",
    ),
    _ContactData(
        "Acme Corporation",
        "Alex",
        "Kamal",
        "alex.kamal@acme.example.com",
        "Procurement Manager",
        "Finance",
        "+1-555-201-0005",
    ),
    # Globex Industries (3)
    _ContactData(
        "Globex Industries", "Hank", "Scorpio", "hank.scorpio@globex.example.com", "CEO", "Executive", "+1-555-202-0001"
    ),
    _ContactData(
        "Globex Industries",
        "Liz",
        "Blake",
        "liz.blake@globex.example.com",
        "HSE Manager",
        "Operations",
        "+1-555-202-0002",
    ),
    _ContactData(
        "Globex Industries",
        "Tom",
        "Greer",
        "tom.greer@globex.example.com",
        "Business Development",
        "Sales",
        "+1-555-202-0003",
    ),
    # Stark Enterprises (4)
    _ContactData(
        "Stark Enterprises",
        "Tony",
        "Stark",
        "tony.stark@stark.example.com",
        "CEO & CTO",
        "Executive",
        "+1-555-203-0001",
    ),
    _ContactData(
        "Stark Enterprises", "Pepper", "Potts", "pepper.potts@stark.example.com", "COO", "Executive", "+1-555-203-0002"
    ),
    _ContactData(
        "Stark Enterprises",
        "Phil",
        "Coulson",
        "phil.coulson@stark.example.com",
        "Head of Security",
        "Security",
        "+1-555-203-0003",
    ),
    _ContactData(
        "Stark Enterprises",
        "Happy",
        "Hogan",
        "happy.hogan@stark.example.com",
        "Personal Driver",
        "Operations",
        "+1-555-203-0004",
    ),
    # Wayne Industries (3)
    _ContactData(
        "Wayne Industries", "Bruce", "Wayne", "bruce.wayne@wayne.example.com", "CEO", "Executive", "+1-555-204-0001"
    ),
    _ContactData("Wayne Industries", "Lucius", "Fox", "lucius.fox@wayne.example.com", "CTO", "R&D", "+1-555-204-0002"),
    _ContactData(
        "Wayne Industries",
        "Alfred",
        "Pennyworth",
        "alfred.pennyworth@wayne.example.com",
        "Executive Assistant",
        "Executive",
        "+1-555-204-0003",
    ),
    # Umbrella Corp (2)
    _ContactData(
        "Umbrella Corp",
        "Albert",
        "Wesker",
        "albert.wesker@umbrella.example.com",
        "Research Director",
        "R&D",
        "+44-20-7946-1001",
    ),
    _ContactData(
        "Umbrella Corp",
        "Jill",
        "Valentine",
        "jill.valentine@umbrella.example.com",
        "Security Analyst",
        "Security",
        "+44-20-7946-1002",
    ),
    # Initech Solutions (2)
    _ContactData(
        "Initech Solutions",
        "Bill",
        "Lumbergh",
        "bill.lumbergh@initech.example.com",
        "VP of Engineering",
        "Engineering",
        "+1-555-206-0001",
    ),
    _ContactData(
        "Initech Solutions",
        "Peter",
        "Gibbons",
        "peter.gibbons@initech.example.com",
        "Software Engineer",
        "Engineering",
        "+1-555-206-0002",
    ),
    # Weyland-Yutani (3)
    _ContactData(
        "Weyland-Yutani",
        "Ellen",
        "Ripley",
        "ellen.ripley@weyland.example.com",
        "Director of Operations",
        "Operations",
        "+1-555-207-0001",
    ),
    _ContactData(
        "Weyland-Yutani",
        "Burke",
        "Carter",
        "burke.carter@weyland.example.com",
        "Corporate Liaison",
        "Executive",
        "+1-555-207-0002",
    ),
    _ContactData(
        "Weyland-Yutani",
        "David",
        "Bishop",
        "david.bishop@weyland.example.com",
        "Science Officer",
        "R&D",
        "+1-555-207-0003",
    ),
    # Pied Piper (2)
    _ContactData(
        "Pied Piper",
        "Richard",
        "Hendricks",
        "richard.hendricks@piedpiper.example.com",
        "CEO",
        "Executive",
        "+1-555-208-0001",
    ),
    _ContactData(
        "Pied Piper",
        "Gilfoyle",
        "Bertram",
        "gilfoyle@piedpiper.example.com",
        "Systems Architect",
        "Engineering",
        "+1-555-208-0002",
    ),
    # Dunder Mifflin (3)
    _ContactData(
        "Dunder Mifflin",
        "Michael",
        "Scott",
        "michael.scott@dundermifflin.example.com",
        "Regional Manager",
        "Executive",
        "+1-555-210-0001",
    ),
    _ContactData(
        "Dunder Mifflin",
        "Dwight",
        "Schrute",
        "dwight.schrute@dundermifflin.example.com",
        "Assistant Manager",
        "Sales",
        "+1-555-210-0002",
    ),
    _ContactData(
        "Dunder Mifflin",
        "Jim",
        "Halpert",
        "jim.halpert@dundermifflin.example.com",
        "Sales Representative",
        "Sales",
        "+1-555-210-0003",
    ),
    # Oscorp (3)
    _ContactData(
        "Oscorp", "Norman", "Osborn", "norman.osborn@oscorp.example.com", "CEO", "Executive", "+1-555-213-0001"
    ),
    _ContactData(
        "Oscorp", "Harry", "Osborn", "harry.osborn@oscorp.example.com", "Chief of Research", "R&D", "+1-555-213-0002"
    ),
    _ContactData("Oscorp", "Gwen", "Stacy", "gwen.stacy@oscorp.example.com", "Lab Director", "R&D", "+1-555-213-0003"),
    # LexCorp (2)
    _ContactData("LexCorp", "Lex", "Luthor", "lex.luthor@lexcorp.example.com", "CEO", "Executive", "+1-555-214-0001"),
    _ContactData(
        "LexCorp",
        "Mercy",
        "Graves",
        "mercy.graves@lexcorp.example.com",
        "Chief of Staff",
        "Executive",
        "+1-555-214-0002",
    ),
    # Capsule Corporation (2)
    _ContactData(
        "Capsule Corporation",
        "Bulma",
        "Briefs",
        "bulma.briefs@capsule.example.com",
        "Director of R&D",
        "R&D",
        "+81-3-0000-2001",
    ),
    _ContactData(
        "Capsule Corporation",
        "Vegeta",
        "Briefs",
        "vegeta.briefs@capsule.example.com",
        "Head of Testing",
        "Engineering",
        "+81-3-0000-2002",
    ),
    # Tyrell Corporation (3)
    _ContactData(
        "Tyrell Corporation",
        "Eldon",
        "Tyrell",
        "eldon.tyrell@tyrell.example.com",
        "Founder & CEO",
        "Executive",
        "+1-555-217-0001",
    ),
    _ContactData(
        "Tyrell Corporation",
        "Rachael",
        "Tyrell",
        "rachael.tyrell@tyrell.example.com",
        "Research Lead",
        "R&D",
        "+1-555-217-0002",
    ),
    _ContactData(
        "Tyrell Corporation",
        "J.F.",
        "Sebastian",
        "jf.sebastian@tyrell.example.com",
        "Genetic Designer",
        "R&D",
        "+1-555-217-0003",
    ),
    # Momcorp (2)
    _ContactData(
        "Momcorp", "Carol", "Miller", "carol.miller@momcorp.example.com", "CEO (Mom)", "Executive", "+1-555-218-0001"
    ),
    _ContactData(
        "Momcorp",
        "Walter",
        "Miller",
        "walter.miller@momcorp.example.com",
        "VP of Supply Chain",
        "Operations",
        "+1-555-218-0002",
    ),
    # Vandelay Industries (2)
    _ContactData(
        "Vandelay Industries",
        "Art",
        "Vandelay",
        "art.vandelay@vandelay.example.com",
        "Founder",
        "Executive",
        "+1-555-220-0001",
    ),
    _ContactData(
        "Vandelay Industries",
        "George",
        "Costanza",
        "george.costanza@vandelay.example.com",
        "Importer/Exporter",
        "Sales",
        "+1-555-220-0002",
    ),
    # Hooli (2)
    _ContactData("Hooli", "Gavin", "Belson", "gavin.belson@hooli.example.com", "CEO", "Executive", "+1-555-209-0001"),
    _ContactData(
        "Hooli",
        "Nelson",
        "Bighetti",
        "nelson.bighetti@hooli.example.com",
        "Head of R&D",
        "Engineering",
        "+1-555-209-0002",
    ),
    # Buy n Large (2)
    _ContactData(
        "Buy n Large",
        "Shelby",
        "Forthright",
        "shelby.forthright@buynlarge.example.com",
        "CEO",
        "Executive",
        "+1-555-211-0001",
    ),
    _ContactData(
        "Buy n Large",
        "Dana",
        "Cross",
        "dana.cross@buynlarge.example.com",
        "Head of Merchandising",
        "Retail",
        "+1-555-211-0002",
    ),
    # Cyberdyne Systems (2)
    _ContactData(
        "Cyberdyne Systems",
        "Miles",
        "Dyson",
        "miles.dyson@cyberdyne.example.com",
        "Director of Special Projects",
        "R&D",
        "+1-555-216-0001",
    ),
    _ContactData(
        "Cyberdyne Systems",
        "Sarah",
        "Reynolds",
        "sarah.reynolds@cyberdyne.example.com",
        "VP of Engineering",
        "Engineering",
        "+1-555-216-0002",
    ),
    # Rekall (2)
    _ContactData(
        "Rekall",
        "Douglas",
        "Quaid",
        "douglas.quaid@rekall.example.com",
        "Sales Representative",
        "Sales",
        "+1-555-219-0001",
    ),
    _ContactData(
        "Rekall", "Lori", "Quaid", "lori.quaid@rekall.example.com", "Marketing Manager", "Marketing", "+1-555-219-0002"
    ),
]

_LEADS: list[_LeadData] = [
    _LeadData(
        "Aisha",
        "Khan",
        "Nexus Dynamics",
        "aisha.khan@nexusdynamics.example.com",
        "+1-555-300-0001",
        "CTO",
        "Contacted",
        "Web",
        "Technology",
    ),
    _LeadData(
        "Marco",
        "Rossi",
        "FuturePath Analytics",
        "marco.rossi@futurepath.example.com",
        "+39-02-0000-0001",
        "Data Director",
        "Qualified",
        "Conference",
        "Technology",
    ),
    _LeadData(
        "Sofia",
        "Andersson",
        "NordLight Energy",
        "sofia.andersson@nordlight.example.com",
        "+46-8-0000-0001",
        "Head of Procurement",
        "New",
        "Cold Call",
        "Energy",
    ),
    _LeadData(
        "Yuki",
        "Tanaka",
        "Sunrise Logistics",
        "yuki.tanaka@sunriselog.example.com",
        "+81-3-0000-3001",
        "Operations Manager",
        "Contacted",
        "Partner Referral",
        "Transportation",
    ),
    _LeadData(
        "Carlos",
        "Mendoza",
        "MedVault Systems",
        "carlos.mendoza@medvault.example.com",
        "+1-555-300-0005",
        "VP of Sales",
        "Qualified",
        "Web",
        "Healthcare",
    ),
    _LeadData(
        "Emily",
        "Johansson",
        "PixelForge Studio",
        "emily.johansson@pixelforge.example.com",
        "+46-8-0000-0002",
        "Creative Director",
        "New",
        "Trade Show",
        "Media",
    ),
    _LeadData(
        "Ravi",
        "Sharma",
        "Apex Consulting",
        "ravi.sharma@apex.example.com",
        "+91-22-0000-0001",
        "Managing Partner",
        "Contacted",
        "Email Campaign",
        "Consulting",
    ),
    _LeadData(
        "Lin",
        "Wei",
        "Horizon Fintech",
        "lin.wei@horizonfintech.example.com",
        "+86-10-0000-0001",
        "Head of Partnerships",
        "Qualified",
        "Web",
        "Finance",
    ),
    _LeadData(
        "James",
        "Okafor",
        "SafeNet Insurance",
        "james.okafor@safenet.example.com",
        "+234-1-000-0001",
        "Product Owner",
        "New",
        "Cold Call",
        "Insurance",
    ),
    _LeadData(
        "Marie",
        "Dupont",
        "CloudBridge SaaS",
        "marie.dupont@cloudbridge.example.com",
        "+33-1-0000-0001",
        "Head of Growth",
        "Contacted",
        "Partner Referral",
        "Technology",
    ),
    _LeadData(
        "Tariq",
        "Al-Rashid",
        "Sandstone Capital",
        "tariq.alrashid@sandstone.example.com",
        "+971-4-000-0001",
        "Investment Director",
        "Qualified",
        "Conference",
        "Finance",
    ),
    _LeadData(
        "Hannah",
        "Müller",
        "AutoDrive GmbH",
        "hannah.muller@autodrive.example.com",
        "+49-30-0000-0001",
        "Product Manager",
        "New",
        "Web",
        "Automotive",
    ),
    _LeadData(
        "Priya",
        "Nair",
        "BioClean Labs",
        "priya.nair@bioclean.example.com",
        "+91-80-0000-0001",
        "Research Manager",
        "Contacted",
        "Email Campaign",
        "Biotechnology",
    ),
    _LeadData(
        "Leon",
        "Beaumont",
        "EcoBuild Paris",
        "leon.beaumont@ecobuild.example.com",
        "+33-1-0000-0002",
        "Sustainability Director",
        "Unqualified",
        "Trade Show",
        "Construction",
    ),
    _LeadData(
        "Kenji",
        "Watanabe",
        "DataStream Japan",
        "kenji.watanabe@datastream.example.com",
        "+81-3-0000-3002",
        "Analytics Lead",
        "Qualified",
        "Web",
        "Technology",
    ),
    _LeadData(
        "Fatima",
        "Al-Sayed",
        "GreenWave Energy",
        "fatima.alsayed@greenwave.example.com",
        "+966-1-0000-0001",
        "VP Operations",
        "New",
        "Cold Call",
        "Energy",
    ),
    _LeadData(
        "Lucas",
        "Petrov",
        "FinEdge Services",
        "lucas.petrov@finedge.example.com",
        "+7-495-000-0001",
        "Account Director",
        "Contacted",
        "Conference",
        "Finance",
    ),
    _LeadData(
        "Chloe",
        "Martin",
        "RetailNow France",
        "chloe.martin@retailnow.example.com",
        "+33-1-0000-0003",
        "Head of Buying",
        "Unqualified",
        "Web",
        "Retail",
    ),
    _LeadData(
        "Amara",
        "Diallo",
        "Saheltech Solutions",
        "amara.diallo@saheltech.example.com",
        "+221-33-000-0001",
        "Co-Founder",
        "New",
        "Partner Referral",
        "Technology",
    ),
    _LeadData(
        "Ben",
        "Collins",
        "SwiftShip Logistics",
        "ben.collins@swiftship.example.com",
        "+44-20-7946-2001",
        "VP of Sales",
        "Qualified",
        "Email Campaign",
        "Transportation",
    ),
    _LeadData(
        "Nadia",
        "Volkov",
        "CryptoSecure Lab",
        "nadia.volkov@cryptosecure.example.com",
        "+7-495-000-0002",
        "Security Architect",
        "Contacted",
        "Conference",
        "Technology",
    ),
    _LeadData(
        "Diego",
        "Ramirez",
        "AgriTech Mesoamerica",
        "diego.ramirez@agritech.example.com",
        "+52-55-0000-0001",
        "Business Dev Manager",
        "New",
        "Trade Show",
        "Agriculture",
    ),
    _LeadData(
        "Sun",
        "Jing",
        "MegaStore China",
        "sun.jing@megastore.example.com",
        "+86-21-0000-0001",
        "Procurement Director",
        "Qualified",
        "Web",
        "Retail",
    ),
    _LeadData(
        "Ivan",
        "Novak",
        "Astro Robotics",
        "ivan.novak@astrorob.example.com",
        "+420-2-0000-001",
        "CTO",
        "Qualified",
        "Partner Referral",
        "Robotics",
    ),
    _LeadData(
        "Leila",
        "Hassan",
        "NileNet Telecom",
        "leila.hassan@nilenet.example.com",
        "+20-2-0000-0001",
        "Regional Director",
        "New",
        "Cold Call",
        "Telecommunications",
    ),
    _LeadData(
        "Oliver",
        "Grant",
        "PurePulse Health",
        "oliver.grant@purepulse.example.com",
        "+44-20-7946-2002",
        "Head of Sales",
        "Contacted",
        "Email Campaign",
        "Healthcare",
    ),
    _LeadData(
        "Mei",
        "Huang",
        "QuantumLeap AI",
        "mei.huang@quantumleap.example.com",
        "+886-2-0000-0001",
        "AI Research Director",
        "Qualified",
        "Conference",
        "Technology",
    ),
    _LeadData(
        "Ethan",
        "Brooks",
        "SkyVault Storage",
        "ethan.brooks@skyvault.example.com",
        "+1-555-300-0028",
        "Infrastructure Lead",
        "New",
        "Web",
        "Technology",
    ),
    _LeadData(
        "Amina",
        "Traoré",
        "SolarEdge Africa",
        "amina.traore@solaredge.example.com",
        "+225-20-000-001",
        "Partnerships Director",
        "Contacted",
        "Trade Show",
        "Energy",
    ),
    _LeadData(
        "Hiroshi",
        "Kato",
        "NanoTech Kyoto",
        "hiroshi.kato@nanotech.example.com",
        "+81-75-000-0001",
        "VP Engineering",
        "Unqualified",
        "Cold Call",
        "Technology",
    ),
]


_ROLES: list[_RoleData] = [
    _RoleData("Executive", "C-suite and VP-level executives with full visibility."),
    _RoleData("Sales Manager", "Manages the sales team and approves deals."),
    _RoleData("Sales Representative", "Handles direct sales, accounts, and opportunities."),
    _RoleData("Account Manager", "Manages ongoing customer relationships."),
    _RoleData("Support Agent", "Handles customer cases and support tickets."),
]

_OPPORTUNITIES: list[_OpportunityData] = [
    _OpportunityData("Acme Platform Expansion", "Acme Corporation", "Proposal/Price Quote", 125_000, "2025-09-30"),
    _OpportunityData("Globex Energy Suite", "Globex Industries", "Value Proposition", 320_000, "2025-08-15"),
    _OpportunityData("Stark AI Integration", "Stark Enterprises", "Perception Analysis", 540_000, "2025-10-31"),
    _OpportunityData("Wayne Security Upgrade", "Wayne Industries", "Closed Won", 180_000, "2025-06-01"),
    _OpportunityData("Initech SaaS Migration", "Initech Solutions", "Needs Analysis", 65_000, "2025-11-15"),
    _OpportunityData("Weyland Field Ops Tools", "Weyland-Yutani", "Id. Decision Makers", 275_000, "2025-12-01"),
    _OpportunityData("Pied Piper Dev Platform", "Pied Piper", "Qualification", 42_000, "2025-09-01"),
    _OpportunityData("Dunder Mifflin CRM", "Dunder Mifflin", "Prospecting", 28_000, "2025-10-01"),
    _OpportunityData("Oscorp Biotech Analytics", "Oscorp", "Proposal/Price Quote", 210_000, "2025-07-31"),
    _OpportunityData("LexCorp Grid Monitoring", "LexCorp", "Value Proposition", 390_000, "2025-11-01"),
    _OpportunityData("Capsule ERP Rollout", "Capsule Corporation", "Closed Won", 480_000, "2025-05-15"),
    _OpportunityData("Cyberdyne AI Contract", "Cyberdyne Systems", "Needs Analysis", 150_000, "2026-01-15"),
    _OpportunityData("Tyrell Biodata Platform", "Tyrell Corporation", "Proposal/Price Quote", 620_000, "2025-08-30"),
    _OpportunityData("Momcorp Fleet Mgmt", "Momcorp", "Closed Won", 730_000, "2025-04-30"),
    _OpportunityData("Hooli Enterprise Deal", "Hooli", "Prospecting", 900_000, "2026-03-01"),
]

_CASES: list[_CaseData] = [
    _CaseData(
        "Integration API returning 500 on bulk import",
        "Acme Corporation",
        "The bulk import endpoint fails intermittently under load.",
        "Open",
        "High",
        "Web",
    ),
    _CaseData(
        "Dashboard charts not loading for EU users",
        "Globex Industries",
        "Users in the EU region report blank dashboards.",
        "In Progress",
        "Medium",
        "Email",
    ),
    _CaseData(
        "Billing discrepancy on March invoice",
        "Stark Enterprises",
        "Invoice shows incorrect quantity for premium seats.",
        "Open",
        "High",
        "Phone",
    ),
    _CaseData(
        "Password reset email not received",
        "Wayne Industries",
        "Multiple users unable to request password reset.",
        "Closed",
        "Medium",
        "Email",
    ),
    _CaseData(
        "Feature request: bulk CSV export",
        "Initech Solutions",
        "Customer wants to export records as CSV from the UI.",
        "Open",
        "Low",
        "Web",
    ),
    _CaseData(
        "Mobile app crashes on login",
        "Weyland-Yutani",
        "Android app crashes immediately after entering credentials.",
        "In Progress",
        "Critical",
        "Phone",
    ),
    _CaseData(
        "SAML SSO configuration assistance",
        "Oscorp",
        "Need help setting up SAML 2.0 SSO with Azure AD.",
        "Open",
        "Medium",
        "Email",
    ),
    _CaseData(
        "Report scheduler not firing",
        "LexCorp",
        "Scheduled reports stopped sending after the last update.",
        "Closed",
        "High",
        "Web",
    ),
    _CaseData(
        "Data migration from legacy system",
        "Capsule Corporation",
        "Assistance needed migrating 50k records from old CRM.",
        "Open",
        "Medium",
        "Partner",
    ),
    _CaseData(
        "Performance degradation on large account views",
        "Tyrell Corporation",
        "Account detail pages time out with 10k+ contacts.",
        "In Progress",
        "High",
        "Web",
    ),
]


# ---------------------------------------------------------------------------
# Seeding orchestration
# ---------------------------------------------------------------------------


async def seed_demo_data(db: AsyncSession, admin_user: User) -> None:
    """Populate the database with demo CRM data.

    Does nothing when ``settings.seed_demo_data`` is ``False`` or when the
    sentinel account already exists (idempotency guard).
    """
    if not settings.seed_demo_data:
        logger.info("Demo data seeding is disabled (SEED_DEMO_DATA is not set). Skipping.")
        return

    # Idempotency check
    result = await db.execute(select(Account).where(Account.name == _SENTINEL_ACCOUNT, Account.is_deleted.is_(False)))
    if result.scalars().first() is not None:
        logger.info("Demo data already present — skipping.")
        return

    admin_id = admin_user.id
    audit = {"owner_id": admin_id, "created_by_id": admin_id, "updated_by_id": admin_id}

    # ------------------------------------------------------------------
    # Accounts
    # ------------------------------------------------------------------
    account_map: dict[str, Account] = {}
    for a in _ACCOUNTS:
        account = Account(
            name=a.name,
            type=a.type,
            industry=a.industry,
            website=a.website,
            phone=a.phone,
            billing_city=a.billing_city,
            billing_country=a.billing_country,
            annual_revenue=a.annual_revenue,
            number_of_employees=a.number_of_employees,
            description=a.description,
            **audit,
        )
        db.add(account)
        account_map[a.name] = account

    await db.flush()  # populate IDs before contacts reference them

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------
    for c in _CONTACTS:
        parent = account_map.get(c.account_name)
        contact = Contact(
            account_id=parent.id if parent else None,
            first_name=c.first_name,
            last_name=c.last_name,
            email=c.email,
            title=c.title,
            department=c.department,
            phone=c.phone,
            **audit,
        )
        db.add(contact)

    # ------------------------------------------------------------------
    # Leads
    # ------------------------------------------------------------------
    for lead_data in _LEADS:
        lead = Lead(
            first_name=lead_data.first_name,
            last_name=lead_data.last_name,
            company=lead_data.company,
            email=lead_data.email,
            phone=lead_data.phone,
            title=lead_data.title,
            status=lead_data.status,
            lead_source=lead_data.lead_source,
            industry=lead_data.industry,
            **audit,
        )
        db.add(lead)

    await db.flush()

    # ------------------------------------------------------------------
    # Roles
    # ------------------------------------------------------------------
    for r in _ROLES:
        role = Role(
            name=r.name,
            description=r.description,
            **audit,
        )
        db.add(role)

    # ------------------------------------------------------------------
    # Opportunities
    # ------------------------------------------------------------------
    from datetime import date  # noqa: PLC0415

    for o in _OPPORTUNITIES:
        parent = account_map.get(o.account_name)
        opp = Opportunity(
            name=o.name,
            account_id=parent.id if parent else None,
            stage=o.stage,
            amount=o.amount,
            close_date=date.fromisoformat(o.close_date),
            **audit,
        )
        db.add(opp)

    # ------------------------------------------------------------------
    # Cases
    # ------------------------------------------------------------------
    for c_data in _CASES:
        parent = account_map.get(c_data.account_name)
        case = Case(
            subject=c_data.subject,
            account_id=parent.id if parent else None,
            description=c_data.description,
            status=c_data.status,
            priority=c_data.priority,
            origin=c_data.origin,
            case_number=await _generate_case_number(db),
            **audit,
        )
        db.add(case)

    await db.flush()
    logger.info(
        "Demo data seeded — %d accounts, %d contacts, %d leads, %d opportunities, %d cases, %d roles.",
        len(_ACCOUNTS),
        len(_CONTACTS),
        len(_LEADS),
        len(_OPPORTUNITIES),
        len(_CASES),
        len(_ROLES),
    )
