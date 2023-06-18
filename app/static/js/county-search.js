// undefined class error??

function fillSelectOption(option_value, option_name) {
  optionText = '<option value="' + option_value + '">' + option_name + '</option>';
  return optionText;
}

$(document).ready(function() {
  $("#state_postal").change(function() {
    let state_postal = $("#state_postal").val();
    $.ajax({
        type: 'GET',
        contentType: "application/json",
        url: "/" + state_postal + "/counties",
        success: function(data) {
          optionText = '';
          // console.log(data.county_names);
          for (var county of data.county_names) {
            optionText += fillSelectOption(county, county);
          }
          $("#county_name").html(optionText);
        }
    })
  })
})
