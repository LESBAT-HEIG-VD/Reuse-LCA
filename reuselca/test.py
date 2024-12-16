function
updateGraph()
{
    var
unit = document.getElementById("unit-select").value;
var
url;

if (unit === "tonnes")
{
    url = '{imp_tot_comparing_tonnes}';
} else if (unit === "kg_per_m2") {
url = '{imp_tot_comparing_kg_per_m2}';
} else if (unit == = "kg_per_m2_per_year") {
url = '{imp_tot_comparing_kg_per_m2_per_year}';
}

document.getElementById("bar_comparison").src = url;
}