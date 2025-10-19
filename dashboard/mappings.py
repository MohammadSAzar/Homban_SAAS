from . import forms


RELATED_MODELS = {
    'sf': ('new_sale_file', forms.SaleFileStatusForm),
    'rf': ('new_rent_file', forms.RentFileStatusForm),
    'by': ('new_buyer', forms.BuyerStatusForm),
    'rt': ('new_renter', forms.RenterStatusForm),
    'ps': ('new_person', forms.PersonStatusForm),
}

