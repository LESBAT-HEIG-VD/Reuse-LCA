def get_rating_dot(rating):
    if rating == "Project specific":
        return '<span style="color: #57e32c;" class="data-rating-dot">&bull;</span>'
    elif rating == "Not concerned":
        return '<span style="color: #57e32c;" class="data-rating-dot">&bull;</span>'
    elif rating == "Estimate":
        return '<span style="color: #b7dd29;" class="data-rating-dot">&bull;</b></span>'
    elif rating == "Hypothesis":
        return '<span style="color: #ffe234;" class="data-rating-dot">&bull;</b></span>'
    elif rating == "Default (no data)":
        return '<span style="color: #ffa534;" class="data-rating-dot">&bull;</b></span>'
    elif rating == "Not modelled (no data)":
        return '<span style="color: #ff4545;" class="data-rating-dot">&bull;</b></span>'
