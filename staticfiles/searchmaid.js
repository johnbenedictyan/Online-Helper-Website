/*global $*/

var send_data = {};

$(document).ready(function() {
    // reset all parameters on page load
    resetFilters();

    // store all GET parameters in queryDict
    var queryDict = {}
    location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]})
    for(var key in queryDict) {
        queryDict[key] = decodeURIComponent(queryDict[key])
    }

    // Load GET parameters into search query if they exist
    if(queryDict['preferred_responsibility'] && queryDict['preferred_responsibility'] != 'none'){
        send_data['preferred_responsibility'] = queryDict['preferred_responsibility']
        $('#input_preferred_responsibility').val(queryDict['preferred_responsibility'])
    }
    if(queryDict['nationality'] && queryDict['nationality'] != 'none'){
        send_data['nationality'] = queryDict['nationality']
        $('#inputNationality').val(queryDict['nationality'])
    }
    if(queryDict['type_of_maid'] && queryDict['type_of_maid'] != 'none'){
        send_data['type_of_maid'] = queryDict['type_of_maid']
        $('#input_type_of_maid').val(queryDict['type_of_maid'])
    }

    // Load data base on settings
    getAPIData();
    // get all info from database via 
    // AJAX call into info select options

    // on selecting the last updated option
    $('#input_last_updated').on('change', function() {
        // update the selected Nationality
        if (this.value == "none")
            send_data['last_updated'] = "";
        else
            send_data['last_updated'] = this.value;
        getAPIData();
    });

    // on selecting the Nationality option
    $('#inputNationality').on('change', function() {
        // update the selected Nationality
        if (this.value == "none")
            send_data['nationality'] = "";
        else
            send_data['nationality'] = this.value;
        getAPIData();
    });

    // on filtering the type_of_maid input
    $('#input_type_of_maid').on('change', function() {
        // get the api data of updated type_of_maid
        if (this.value == "none")
            send_data['type_of_maid'] = "";
        else
            send_data['type_of_maid'] = this.value;
        getAPIData();
    });

    // on filtering the preferred_responsibility input
    $('#input_preferred_responsibility').on('change', function() {
        // get the api data of updated preferred_responsibility
        if (this.value == "none")
            send_data['preferred_responsibility'] = "";
        else
            send_data['preferred_responsibility'] = this.value;
        getAPIData();
    });

    // on filtering the input_language_ability input
    $('#input_language_ability').on('change', function() {
        // get the api data of updated language_ability
        if (this.value == "none")
            send_data['language_ability'] = "";
        else
            send_data['language_ability'] = this.value;
        getAPIData();
    });

    // on filtering the marital_status input
    $('#input_marital_status').on('change', function() {
        // get the api data of updated marital_status
        if (this.value == "none")
            send_data['marital_status'] = "";
        else
            send_data['marital_status'] = this.value;
        getAPIData();
    });

    // on filtering the age input
    $('#input_age_group').on('change', function () {
        // get the api data of updated age
        if(this.value == "none")
            send_data['age_group'] = "";
        else
            send_data['age_group'] = this.value;
        getAPIData();
    });

    // on filtering agency name
    $('#input_agency').on('change', function () {
        // get the api data of updated age
        if(this.value == "none")
            send_data['agency'] = "";
        else
            send_data['agency'] = this.value;
        getAPIData();
    });

    // sort the data according to price/points
    $('#sort_by').on('change', function() {
        send_data['sort_by'] = this.value;
        getAPIData();
    });

    // display the results after reseting the filters
    $("#reset_btn btn-xs-lg").click(function() {
        resetFilters();
        getAPIData();
    });
});


/**
    Function that resets all the filters   
**/
function resetFilters() {
    $("#input_last_updated").val("none");
    $("#inputNationality").val("none");
    $("#input_type_of_maid").val("none");
    $("#input_preferred_responsibility").val("none");
    $("#input_language_ability").val("none");
    $("#input_marital_status").val("none");
    $("#input_age_group").val("none");
    $("#input_agency").val("none");

    send_data['last_updated'] = '';
    send_data['nationality'] = '';
    send_data['type_of_maid'] = '';
    send_data['preferred_responsibility'] = '';
    send_data['language_ability'] = '';
    send_data['marital_status'] = '';
    send_data['age_group'] = '';
    send_data['agency'] = '';
    send_data['format'] = 'json';
}

/**.
    Utility function to showcase the api data 
    we got from backend to the table content
**/
function putCards(result) {
    // creating table row for each result and
    // pushing to the html cntent of table body of listing table
    let card;
    if(result.results.length > 0){
        $("#maid_cards").show();
        $("#maid_cards").html("");
        $("#results_count").html(result.length)
        $.each(result['results'], function (a, b) {
              card = `<div class="card mb-3 ml-2 mr-2 mt-3 display" style="width: 14rem">
                        <a class="text-decoration-none" href="/maid_info/` + b.id + `">
                            <img src="` + b.maid_photo + `" class="card-img-top">
                        <ul class="list-group list-group-flush card-deck-margin" style="font-weight: 500">
                            <li class="list-group-item sm-padding">
                                <h4 class="card-title maid-name" style="color:#234c7a">` + b.name + `</h4>
                                <p class="card-text text-left">` + b.nationality + `</p>
                            </li>
                            <li class="list-group-item sm-padding">
                                    <p class="card-text text-left">` + b.age + ` Yrs old / ` + b.marital_status + `</p>
                            </li>
                            <li class="list-group-item sm-padding">
                                    <p class="card-text text-left">` + b.type_of_maid + `</p>
                            </li>
                        </ul>
                        </a>
                    <a type="button" class="btn btn-xs-lg lightblue-btn btn-xs-lg btn btn-xs-lg-block shadow" href="/shortlisted_cart/add_to_shortlisted_cart/` + b.id + `">Add to Shortlist</a>
                </div>
                
                <div class="popup shadow-dark">
                <h3 style="color:#234c7a; font-weight:600;">` + b.agency_name + `</h3>`
                if(b['employment_history'].length != 0){
                    card += `<h6 style="padding: 5px; background: #888888; color: white">Employment History</h6>`
                }
                b['employment_history'].forEach(history => {
                    card += `<p><b>${history['date_from']} - ${history['date_to']}</b></p>`+
                    `<p>Country: ${history['country']} | Employer: ${history['employer']}</p>`+
                    `<p class="text-left">${history['work_duties']}</p>`+
                    `<p class="text-left">${history['remarks']}</p>`
                })
				card += `<p><small>Updated on ` + b.dateupdated + `</small></p>
				</div>`;
            $("#maid_cards").append(card);
            
            let popoverShowing = false;
            $('.display').hover(function() {
                if (!popoverShowing) {

                    let popup = $(this).next();
                    popup.css('display', 'block');
                    let buttonTop = $(this).position().top;
                    let buttonLeft = $(this).position().left;
                    let position = buttonLeft + 600;
                    let screenWidth = $(window).width() - 250;
                    // if buttonLeft + width of the box < right side of the screen, you do the below
                    if (position < screenWidth) {
                        popup.css('top', (buttonTop - 10) + "px");
                        popup.css('left', (buttonLeft + 200) + "px");
                    }
                    else {
                        // if exceed
                        // buttonLeft - 400
                        popup.css('top', (buttonTop - 10) + "px");
                        popup.css('left', (buttonLeft - 380) + "px");
                    }
                    // console.log(position)
                    // console.log(screenWidth)
                }

            }, function() {
                let popoverShowing = true;
                let popup = $(this).next();

                popup.css('display', 'none');
            });

        });
    }
    else {
        $("#maid_cards").hide();
        $("#results_count").html("No");
    }
    // setting previous and next page url for the given result
    let prev_url = result["previous"];
    let next_url = result["next"];
    // let page_url = result["html"]["page_links"];
    // let page_number = result['page_number'];
    // if (prev_url)
    //     prev_url = prev_url.replace("http", "https");
    // if (next_url)
    //     next_url = next_url.replace("http", "https");
    // disabling-enabling button depending on existence of next/prev page. 
    if (prev_url === null) {
        $("#previous").addClass("disabled");
        $("#previous").prop('disabled', true);
    }
    else {
        $("#previous").removeClass("disabled");
        $("#previous").prop('disabled', false);
    }
    if (next_url === null) {
        $("#next").addClass("disabled");
        $("#next").prop('disabled', true);
    }
    else {
        $("#next").removeClass("disabled");
        $("#next").prop('disabled', false);
    }
    // setting the url
    $("#previous").attr("url", prev_url);
    $("#next").attr("url", next_url);
    // displaying result count
    $("#result-count span").html(result["count"]);
    // console.log(page_url);
    $('.temp-page-link').remove();
    // for (let i = 0; i < page_url.length; i++) {
    //     console.log(page_url[i]);
    //     if (page_url[i][0]) {
    //         $("#next-link").before('<li class="pages"><a class="page-link temp-page-link" href="' + page_url[i][0] + '">' + (page_url[i][1]) + '</a></li>');
    //     }
    //     else {
    //         $('#next-link').before('<li class="pages temp-page-link"><a href="#">....<a></li>')
    //     }
    // }
    $(".page-number-item").remove()
    result['html']['page_links'].slice().reverse().forEach((entry) => {
        var active = ""
        if(entry[2]){
            active = "active"
        }
        $("#page-number .page-item:first").after(`<li class="page-item page-number-item ${active}"><button class="btn btn-xs-lg page-link" id="page_no_${entry[1]}" url="${entry[0]}">${entry[1]}</button></li>`)
        console.log(`placing page ${entry[1]}`)
        if(!entry[2]){
            $(`#page_no_${entry[1]}`).click(function() {
                let url = $(this).attr("url");
                console.log(url)
                if (!url)
                    $(this).prop('all', true);
            
                $(this).prop('all', false);
                $.ajax({
                    method: 'GET',
                    url: url,
                    success: function(result) {
                        putCards(result);
                    },
                    error: function(response) {
                        console.log(response)
                    }
                });
            }) // Duplicate code from #next, #previous click() function, will figure out how to condense them.   
        }
    })
}

function getAPIData() {
    let url = $('#maid_cards').attr("url");
    console.log(url);
    $.ajax({
        method: 'GET',
        url: url,
        data: send_data,
        beforeSend: function() {},
        success: function(result) {
            console.log(result);
            putCards(result);
        },
        error: function(response) {
            $("#maid_cards").hide();
        }
    });
}

$("#next, #previous").click(function() {
    let url = $(this).attr("url");
    console.log(url)
    if (!url)
        $(this).prop('all', true);

    $(this).prop('all', false);
    $.ajax({
        method: 'GET',
        url: url,
        success: function(result) {
            putCards(result);
        },
        error: function(response) {
            console.log(response)
        }
    });
})


// $("#page-number").on('click', '.page-link', function(e) {
//     e.preventDefault();
//     let url = $(this).attr("href").replace('http', 'https');
//     console.log(url)
//     if (!url)
//         $(this).prop('all', true);

//     $(this).prop('all', false);
//     $.ajax({
//         method: 'GET',
//         url: url,
//         success: function(result) {
//             putCards(result);
//         },
//         error: function(response) {
//             console.log(response)
//         }
//     });
// })
