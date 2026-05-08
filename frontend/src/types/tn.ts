export interface TnEntry {
  id: number
  name: string
  family: string
  tn_group: string
  synonyms: string | null
  isoform: string | null
  accession_number: string | null

  origin: string | null
  mge_type: string | null
  related_elements: string | null

  length: number | null
  ir: string | null
  dr: number | null
  orf: string | null
  irl: string | null
  irr: string | null
  left_flank: string | null
  right_flank: string | null

  transposition: string | null
  direct_repeat: string | null

  dna_sequence: string | null

  orf1_name: string | null
  orf1_length: number | null
  orf1_begin: number | null
  orf1_end: number | null
  orf1_strand: string | null
  orf1_fusion_orf: string | null
  orf1_function: string | null
  orf1_chemistry: string | null
  orf1_sequence: string | null

  orf2_name: string | null
  orf2_length: number | null
  orf2_begin: number | null
  orf2_end: number | null
  orf2_strand: string | null
  orf2_fusion_orf: string | null
  orf2_function: string | null
  orf2_chemistry: string | null
  orf2_sequence: string | null

  status: string
  submitted_by: number | null
  reviewed_by: number | null
  reviewed_at: string | null
  created_at: string
  updated_at: string
}

export interface TnFilter {
  keyword?: string
  family?: string
  tn_group?: string
  origin?: string
  mge_type?: string
  status?: string
  page: number
  page_size: number
}

export interface TnListResponse {
  items: TnEntry[]
  total: number
  page: number
  page_size: number
}
