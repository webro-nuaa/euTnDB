import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models import User, TnEntry, TnFamily

DATABASE_URL = "postgresql+asyncpg://tndb:tndb@localhost:5432/tndb"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


SUPERFAMILIES = [
    {"family": "Tc1-Mariner", "tn_group": "Tc1", "ir": "TA", "dr": 2, "description": "Tc1/Mariner superfamily"},
    {"family": "hAT", "tn_group": "hAT", "ir": "8bp", "dr": 8, "description": "hAT superfamily"},
    {"family": "MuDR", "tn_group": "MuDR", "ir": "100-300bp", "dr": 9, "description": "MuDR/Mutator superfamily"},
    {"family": "EnSpm", "tn_group": "EnSpm", "ir": "13-28bp", "dr": 3, "description": "En/Spm (CACTA) superfamily"},
    {"family": "piggyBac", "tn_group": "piggyBac", "ir": "TTAA", "dr": 4, "description": "piggyBac superfamily"},
    {"family": "P", "tn_group": "P", "ir": "31bp", "dr": 8, "description": "P element superfamily"},
    {"family": "Merlin", "tn_group": "Merlin", "ir": "20-30bp", "dr": 4, "description": "Merlin superfamily"},
    {"family": "Harbinger", "tn_group": "Harbinger", "ir": "20-40bp", "dr": 3, "description": "Harbinger superfamily"},
    {"family": "Transib", "tn_group": "Transib", "ir": "23bp", "dr": 5, "description": "Transib superfamily"},
    {"family": "Helitron", "tn_group": "Helitron", "ir": None, "dr": None, "description": "Helitron superfamily"},
    {"family": "Crypton", "tn_group": "Crypton", "ir": None, "dr": None, "description": "Crypton superfamily"},
    {"family": "Maverick", "tn_group": "Maverick", "ir": None, "dr": None, "description": "Maverick superfamily"},
]

SPECIES_NAMES = [
    "Homo sapiens", "Mus musculus", "Drosophila melanogaster",
    "Danio rerio", "Caenorhabditis elegans", "Gallus gallus",
    "Xenopus tropicalis", "Oryza sativa", "Arabidopsis thaliana",
    "Zea mays", "Saccharomyces cerevisiae", "Anopheles gambiae",
    "Bombyx mori", "Tribolium castaneum", "Strongylocentrotus purpuratus",
    "Ciona intestinalis", "Takifugu rubripes", "Medaka",
    "Aedes aegypti", "Apis mellifera",
]


def random_dna(length: int) -> str:
    return ''.join(random.choices('ATCG', k=length))


def reverse_complement(seq: str) -> str:
    comp = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G'}
    return ''.join(comp.get(c, 'N') for c in reversed(seq))


async def seed():
    async with async_session() as session:
        print("=== Seeding test data ===")

        result = await session.execute(select(User).where(User.username == "admin"))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username="admin",
                email="admin@tndb.org",
                password_hash=get_password_hash("admin123"),
                role="admin",
                institution="euTnDB Project",
                is_active=True,
            )
            session.add(admin)
            await session.flush()
            print(f"  Created admin user (id={admin.id})")
        else:
            print(f"  Admin user already exists (id={admin.id})")

        for sf in SUPERFAMILIES:
            result = await session.execute(select(TnFamily).where(TnFamily.superfamily == sf["family"]))
            if not result.scalar_one_or_none():
                tf = TnFamily(
                    family_id=sf["family"].lower().replace("-", "_"),
                    superfamily=sf["family"],
                )
                session.add(tf)
                print(f"  Created family: {sf['family']}")
        await session.flush()

        statuses = ["approved", "approved", "approved", "approved", "pending", "pending", "rejected"]

        tn_count = 0
        for i in range(1, 151):
            name = f"euTnDB-{i:05d}"
            result = await session.execute(select(TnEntry).where(TnEntry.name == name))
            if result.scalar_one_or_none():
                continue

            sf = random.choice(SUPERFAMILIES)
            seq_len = random.randint(800, 12000)
            sequence = random_dna(seq_len)

            tir_len = random.randint(10, 50)
            irl = random_dna(tir_len)
            irr = reverse_complement(irl)

            status_val = random.choice(statuses)
            species = random.choice(SPECIES_NAMES)
            days_ago = random.randint(1, 365)
            created = datetime.utcnow() - timedelta(days=days_ago)

            autonomous = random.choice([True, False])

            entry = TnEntry(
                name=name,
                family=sf["family"],
                tn_group=sf["tn_group"],
                synonyms=random.choice([None, f"{name}-syn"]),
                isoform=random.choice([None, f"{name}.a"]),
                accession_number=f"ACC{i:06d}",
                origin=species,
                mge_type="TIR" if sf["ir"] else "non-TIR",
                related_elements=random.choice([None, f"euTnDB-{random.randint(1,150):05d}"]),
                length=seq_len,
                ir=sf["ir"],
                dr=sf["dr"],
                orf=random.choice([None, "1", "2"]),
                irl=irl,
                irr=irr,
                left_flank=random_dna(20) if random.random() > 0.3 else None,
                right_flank=random_dna(20) if random.random() > 0.3 else None,
                transposition="cut-and-paste" if sf["ir"] else None,
                direct_repeat=sf["ir"] if sf["ir"] else None,
                dna_sequence=sequence,
                orf1_name="transposase" if autonomous else None,
                orf1_length=random.randint(300, 1200) if autonomous else None,
                orf1_begin=random.randint(50, 200) if autonomous else None,
                orf1_end=random.randint(400, 1400) if autonomous else None,
                orf1_strand=random.choice(["+", "-"]) if autonomous else None,
                orf1_function="transposase" if autonomous else None,
                orf1_chemistry="DDE" if autonomous else None,
                orf1_sequence=random_dna(random.randint(300, 1200)) if autonomous else None,
                status=status_val,
                submitted_by=None,
                reviewed_by=admin.id if status_val != "pending" else None,
                reviewed_at=datetime.utcnow() - timedelta(days=max(0, days_ago - 3)) if status_val != "pending" else None,
                created_at=created,
                updated_at=created,
            )
            session.add(entry)
            tn_count += 1

        await session.commit()
        print(f"\n  Created {tn_count} Tn entries")
        print("=== Seeding complete! ===")
        print("\nLogin credentials:")
        print("  Username: admin    Password: admin123")


if __name__ == "__main__":
    asyncio.run(seed())
