from services.supabase import supabase


def ottieni_mappa_prezzi_catalogo():
    prodotti = supabase.table("catalogo_prodotti").select("nome, prezzo_standard_mq").execute()
    return {p['nome']: (p['prezzo_standard_mq'] or 0) for p in (prodotti.data or [])}


def ottieni_catalogo_prodotti():
    return supabase.table("catalogo_prodotti").select("*").order("nome").execute().data or []


def ottieni_prodotto_per_nome(nome):
    prodotti = supabase.table("catalogo_prodotti").select("*").eq("nome", nome).execute()
    return prodotti.data[0] if prodotti.data else None
