from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models import TnEntry
from app.schemas.common import ApiResponse

router = APIRouter(prefix="/classification", tags=["Classification"])


CLASSIFICATION_TREE = {
    "name": "Transposable Element",
    "children": [
        {
            "name": "Class I: Retrotransposon",
            "code": "RXX",
            "children": [
                {
                    "name": "Retrotransposon (LTR)",
                    "code": "RLX",
                    "children": [
                        {
                            "name": "Copia",
                            "code": "RLC",
                            "aliases": "Ty1-Copia",
                            "typical_tir": "LTR",
                            "typical_tsd": "5 bp",
                        },
                        {
                            "name": "Gypsy",
                            "code": "RLG",
                            "aliases": "Ty3-Gypsy",
                            "typical_tir": "LTR",
                            "typical_tsd": "5 bp",
                        },
                        {
                            "name": "Bel-Pao",
                            "code": "RLB",
                            "typical_tir": "LTR",
                            "typical_tsd": "5 bp",
                        },
                        {
                            "name": "Retrovirus",
                            "code": "RLR",
                            "typical_tir": "LTR",
                            "typical_tsd": "5 bp",
                        },
                        {
                            "name": "ERV",
                            "code": "RLE",
                            "aliases": "Endogenous Retrovirus",
                            "typical_tir": "LTR",
                            "typical_tsd": "5 bp",
                            "children": [
                                {"name": "ERV1", "code": "RLE1"},
                                {"name": "ERV2", "code": "RLE2", "aliases": "ERVK"},
                                {"name": "ERV3", "code": "RLE3", "aliases": "ERVL"},
                                {"name": "ERV4", "code": "RLE4"},
                                {"name": "Lenti", "code": "RLE-Lenti", "aliases": "Lentivirus"},
                            ],
                        },
                        {
                            "name": "DIRS",
                            "code": "RLD",
                            "typical_tir": "LTR (YR)",
                            "typical_tsd": "None",
                            "children": [
                                {"name": "DIRS", "code": "RYD"},
                                {"name": "Ngaro", "code": "RYN"},
                                {"name": "Viper", "code": "RYV"},
                            ],
                        },
                    ],
                },
                {
                    "name": "LINE (non-LTR)",
                    "code": "RIX",
                    "aliases": "Long Interspersed Nuclear Element",
                    "children": [
                        {
                            "name": "Group I",
                            "children": [
                                {"name": "CRE", "code": "RST-CRE"},
                                {"name": "Ambal", "code": "RST-Ambal"},
                                {"name": "Odin", "code": "RST-Odin"},
                            ],
                        },
                        {
                            "name": "Group II",
                            "children": [
                                {
                                    "name": "L1-like",
                                    "code": "RIL",
                                    "children": [
                                        {"name": "L1", "code": "RIL-L1", "aliases": "LINE-1"},
                                        {"name": "Tx1", "code": "RIL-Tx1"},
                                        {"name": "DRE", "code": "RIL-DRE"},
                                        {"name": "Zorro", "code": "RIL-Zorro"},
                                    ],
                                },
                                {
                                    "name": "R1-like",
                                    "children": [
                                        {
                                            "name": "I-Jockey",
                                            "children": [
                                                {"name": "I", "code": "RII"},
                                                {"name": "Jockey", "code": "RIJ"},
                                            ],
                                        },
                                        {
                                            "name": "R1-subgroup",
                                            "children": [
                                                {"name": "R1", "code": "RIT-R1"},
                                                {"name": "LOA", "code": "RIT-LOA"},
                                            ],
                                        },
                                        {
                                            "name": "CR1-group",
                                            "children": [
                                                {"name": "CR1", "code": "RIT-CR1"},
                                                {"name": "L2", "code": "RIT-L2"},
                                                {"name": "Rex-Babar", "code": "RIT-Rex"},
                                            ],
                                        },
                                        {"name": "Tad1", "code": "RIT-Tad1"},
                                    ],
                                },
                                {
                                    "name": "R2-like",
                                    "children": [
                                        {"name": "R2", "code": "RIT-R2"},
                                        {"name": "NeSL", "code": "RIT-NeSL"},
                                        {"name": "Hero", "code": "RIT-Hero"},
                                    ],
                                },
                                {
                                    "name": "R4-like",
                                    "children": [
                                        {"name": "Dong-R4", "code": "RIT-R4"},
                                        {"name": "Dualen", "code": "RIT-Dualen"},
                                        {"name": "Deceiver", "code": "RIT-Deceiver"},
                                    ],
                                },
                                {
                                    "name": "RTE-like",
                                    "code": "RIT",
                                    "children": [
                                        {"name": "RTE", "code": "RIT-RTE"},
                                        {"name": "BovB", "code": "RIT-BovB"},
                                        {"name": "RTE-X", "code": "RIT-RTEX"},
                                    ],
                                },
                                {"name": "Proto-1", "code": "RIT-Proto1"},
                                {"name": "Proto-2", "code": "RIT-Proto2"},
                                {"name": "Genie", "code": "RIT-Genie"},
                            ],
                        },
                    ],
                },
                {
                    "name": "SINE",
                    "code": "RSX",
                    "aliases": "Short Interspersed Nuclear Element",
                    "children": [
                        {
                            "name": "tRNA Promoter",
                            "code": "RST",
                            "aliases": "SINE2",
                            "children": [
                                {"name": "tRNA-Deu", "code": "RST-Deu"},
                                {"name": "tRNA-Core", "code": "RST-Core", "aliases": "MIR-core"},
                                {"name": "tRNA-L1", "code": "RST-L1"},
                                {"name": "tRNA-RTE", "code": "RST-RTE"},
                                {"name": "tRNA-L2", "code": "RST-L2"},
                                {"name": "ID", "code": "RST-ID"},
                            ],
                        },
                        {
                            "name": "7SL RNA Promoter",
                            "code": "RSL",
                            "aliases": "SINE1",
                            "children": [
                                {"name": "Alu", "code": "RSL-Alu"},
                                {"name": "B2", "code": "RSL-B2"},
                                {"name": "B4", "code": "RSL-B4"},
                            ],
                        },
                        {
                            "name": "5S RNA Promoter",
                            "code": "RSS",
                            "aliases": "SINE3",
                            "children": [
                                {"name": "5S-Deu", "code": "RSS-Deu"},
                                {"name": "5S-Core", "code": "RSS-Core"},
                                {"name": "5S-RTE", "code": "RSS-RTE"},
                            ],
                        },
                    ],
                },
                {
                    "name": "SVA",
                    "code": "RSX-SVA",
                    "typical_tir": "None (Composite)",
                    "typical_tsd": "None",
                },
                {
                    "name": "Penelope-like (PLE)",
                    "code": "RPX",
                    "typical_tir": "None (RT+EN)",
                    "typical_tsd": "None",
                    "children": [
                        {"name": "Penelope", "code": "RPP"},
                        {"name": "Athena", "code": "RPP-Athena"},
                        {"name": "Neptune", "code": "RPP-Neptune"},
                        {"name": "Poseidon", "code": "RPP-Poseidon"},
                        {"name": "Naiad", "code": "RPP-Naiad"},
                        {"name": "Chlamys", "code": "RPP-Chlamys"},
                        {"name": "Hydra", "code": "RPP-Hydra"},
                    ],
                },
            ],
        },
        {
            "name": "Class II: DNA Transposon",
            "code": "DXX",
            "children": [
                {
                    "name": "TIR (Transposase)",
                    "code": "DTX",
                    "aliases": "DDE-transposon",
                    "children": [
                        {
                            "name": "Tc1-Mariner",
                            "code": "DTT",
                            "aliases": "IS630/Tc1/Mariner",
                            "typical_tir": "~30 bp",
                            "typical_tsd": "TA",
                            "children": [
                                {"name": "Tc1", "code": "DTT-Tc1"},
                                {"name": "Mariner", "code": "DTT-Mariner"},
                                {"name": "Tc2", "code": "DTT-Tc2"},
                                {"name": "Pogo", "code": "DTT-Pogo"},
                                {"name": "Tigger", "code": "DTT-Tigger"},
                                {"name": "Fot1", "code": "DTT-Fot1"},
                                {"name": "Stowaway", "code": "DTT-Stowaway"},
                                {"name": "ISRm11", "code": "DTT-ISRm11"},
                                {"name": "Tc4", "code": "DTT-Tc4"},
                                {"name": "m44", "code": "DTT-m44"},
                            ],
                        },
                        {
                            "name": "hAT",
                            "code": "DTA",
                            "aliases": "hobo-Activator-Tam3",
                            "typical_tir": "5-17 bp",
                            "typical_tsd": "8 bp",
                            "children": [
                                {"name": "Activator", "code": "DTA-Ac"},
                                {"name": "Charlie", "code": "DTA-Charlie", "aliases": "Buster"},
                                {"name": "Tip100", "code": "DTA-Tip100"},
                                {"name": "Blackjack", "code": "DTA-Blackjack"},
                                {"name": "Tag1", "code": "DTA-Tag1"},
                                {"name": "hobo", "code": "DTA-hobo"},
                                {"name": "Restless", "code": "DTA-Restless"},
                                {"name": "Pegasus", "code": "DTA-Pegasus"},
                            ],
                        },
                        {
                            "name": "Mutator",
                            "code": "DTM",
                            "aliases": "MULE",
                            "typical_tir": "~100-200 bp",
                            "typical_tsd": "9-11 bp",
                            "children": [
                                {"name": "MuDR", "code": "DTM-MuDR"},
                                {"name": "NOF", "code": "DTM-NOF"},
                                {"name": "F", "code": "DTM-F"},
                                {"name": "Ricksha", "code": "DTM-Ricksha"},
                            ],
                        },
                        {
                            "name": "Merlin",
                            "code": "DTE",
                            "typical_tir": "~20 bp",
                            "typical_tsd": "8 bp",
                        },
                        {
                            "name": "Transib",
                            "code": "DTR",
                            "typical_tir": "14-44 bp",
                            "typical_tsd": "5 bp",
                        },
                        {
                            "name": "P",
                            "code": "DTP",
                            "typical_tir": "46 bp",
                            "typical_tsd": "8 bp",
                            "children": [
                                {"name": "P-Fungi", "code": "DTP-Fungi"},
                            ],
                        },
                        {
                            "name": "PiggyBac",
                            "code": "DTB",
                            "typical_tir": "13 bp",
                            "typical_tsd": "TTAA",
                            "children": [
                                {"name": "PiggyBac", "code": "DTB-PB"},
                                {"name": "PiggyBac-A", "code": "DTB-A"},
                                {"name": "PiggyBac-X", "code": "DTB-X"},
                            ],
                        },
                        {
                            "name": "PIF-Harbinger",
                            "code": "DTH",
                            "typical_tir": "14-15 bp",
                            "typical_tsd": "3 bp (TAA/TTA)",
                            "children": [
                                {"name": "Harbinger", "code": "DTH-Harb"},
                                {"name": "HarbS", "code": "DTH-HarbS"},
                                {"name": "ISL2EU", "code": "DTH-ISL2EU"},
                                {"name": "Spy", "code": "DTH-Spy"},
                            ],
                        },
                        {
                            "name": "CACTA",
                            "code": "DTC",
                            "aliases": "EnSpm",
                            "typical_tir": "13-39 bp",
                            "typical_tsd": "2-3 bp",
                            "children": [
                                {"name": "EnSpm", "code": "DTC-EnSpm"},
                                {"name": "Chapaev", "code": "DTC-Chapaev"},
                                {"name": "Chapaev-3", "code": "DTC-Chapaev3"},
                                {"name": "Mirage", "code": "DTC-Mirage"},
                                {"name": "Transib-CACTA", "code": "DTC-Transib"},
                            ],
                        },
                        {
                            "name": "Ginger",
                            "code": "DTX-Ginger",
                            "children": [
                                {"name": "Ginger-1", "code": "DTX-Ginger1"},
                                {"name": "Ginger-2", "code": "DTX-Ginger2"},
                            ],
                        },
                        {
                            "name": "Sola",
                            "code": "DTX-Sola",
                            "children": [
                                {"name": "Sola-1", "code": "DTX-Sola1"},
                                {"name": "Sola-2", "code": "DTX-Sola2"},
                                {"name": "Sola-3", "code": "DTX-Sola3"},
                            ],
                        },
                        {"name": "Kolobok", "code": "DTX-Kolobok"},
                        {"name": "Academ", "code": "DTX-Academ"},
                        {"name": "Zator", "code": "DTX-Zator"},
                        {"name": "Zisupton", "code": "DTX-Zisupton"},
                        {"name": "Dada", "code": "DTX-Dada"},
                        {"name": "Novosib", "code": "DTX-Novosib"},
                        {"name": "IS3EU", "code": "DTX-IS3EU"},
                    ],
                },
                {
                    "name": "Crypton (YR)",
                    "code": "DYX",
                    "aliases": "Y1-transposon",
                    "children": [
                        {
                            "name": "Crypton",
                            "code": "DYC",
                            "typical_tir": "None (YR)",
                            "typical_tsd": "None",
                            "children": [
                                {"name": "Crypton-A", "code": "DYC-A"},
                                {"name": "Crypton-C", "code": "DYC-C"},
                                {"name": "Crypton-F", "code": "DYC-F"},
                                {"name": "Crypton-H", "code": "DYC-H"},
                                {"name": "Crypton-I", "code": "DYC-I"},
                                {"name": "Crypton-S", "code": "DYC-S"},
                                {"name": "Crypton-V", "code": "DYC-V"},
                                {"name": "Crypton-X", "code": "DYC-X"},
                                {"name": "Crypton-R", "code": "DYC-R"},
                            ],
                        },
                    ],
                },
                {
                    "name": "Helitron (RC)",
                    "code": "DHH",
                    "aliases": "Y2-transposon",
                    "typical_tir": "None (RC)",
                    "typical_tsd": "None",
                    "children": [
                        {"name": "Helitron-1", "code": "DHH-1"},
                        {"name": "Helitron-2", "code": "DHH-2"},
                        {"name": "Helentron", "code": "DHH-Helentron"},
                    ],
                },
                {
                    "name": "Maverick (Polinton)",
                    "code": "DMM",
                    "typical_tir": "None (Polinton)",
                    "typical_tsd": "None",
                    "children": [
                        {"name": "Maverick", "code": "DMM-Mav"},
                        {"name": "Maverick-Mavirus", "code": "DMM-Mavirus"},
                    ],
                },
                {
                    "name": "Casposon",
                    "code": "DTX-Casposon",
                    "typical_tir": "TIR",
                    "typical_tsd": "Variable",
                },
            ],
        },
    ],
}


@router.get("/tree")
async def get_classification_tree(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TnEntry.family, func.count(TnEntry.id))
        .where(TnEntry.family != None)
        .group_by(TnEntry.family)
    )
    family_counts = dict(result.all())

    tree = _add_counts(CLASSIFICATION_TREE, family_counts)
    return ApiResponse(data=tree)


@router.get("/superfamilies")
async def get_superfamilies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TnEntry.family, func.count(TnEntry.id))
        .where(TnEntry.family != None)
        .group_by(TnEntry.family)
        .order_by(func.count(TnEntry.id).desc())
    )
    items = []
    for family, count in result.all():
        info = _find_superfamily_info(CLASSIFICATION_TREE, family)
        items.append({
            "name": family,
            "count": count,
            "code": info.get("code", ""),
            "typical_tir": info.get("typical_tir", ""),
            "typical_tsd": info.get("typical_tsd", ""),
        })
    return ApiResponse(data=items)


def _add_counts(node: dict, family_counts: dict) -> dict:
    result = {"name": node["name"]}
    for key in ("code", "aliases", "typical_tir", "typical_tsd"):
        if key in node:
            result[key] = node[key]

    if "children" in node:
        result["children"] = [_add_counts(c, family_counts) for c in node["children"]]
        result["count"] = sum(c.get("count", 0) for c in result["children"])
    else:
        result["count"] = family_counts.get(node["name"], 0)

    return result


def _find_superfamily_info(node: dict, name: str) -> dict:
    if node.get("name") == name:
        return node
    if "children" in node:
        for child in node["children"]:
            found = _find_superfamily_info(child, name)
            if found:
                return found
    return {}
