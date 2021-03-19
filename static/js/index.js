// Mutation Observer Function
const MO = (node_settings, callback_function) => {
    MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

    var observer = new MutationObserver(function (mutations, observer) {
        console.log(mutations, observer);
        callback_function();
    });

    if(node_settings.nodeName){
        observer.observe(
            node_settings.nodeName,
            node_settings.settings
        );
    }
}

// Django Filters range slider
const rangeSliderInitialisation = function(){
    $('.noUi-handle').on('click', function () {
        $(this).width(50);
    });
    var rangeSlider = document.getElementById('slider-range');
    if (rangeSlider != null) {
        const rangeMin = 23;
        const rangeMax = 60;
        const rangeSliderSetting = {
            start: [rangeMin, rangeMax],
            step: 1,
            range: {
                'min': [rangeMin],
                'max': [rangeMax]
            },
            format: wNumb({
                decimals: 0
            }),
            connect: true
        }
        noUiSlider.create(rangeSlider, rangeSliderSetting);

        document.getElementById('id_age_0').value = rangeSliderSetting['range']['min'][0];
        document.getElementById('id_age_1').value = rangeSliderSetting['range']['max'][0];

        // Set visual min and max values and also update value hidden form inputs
        rangeSlider.noUiSlider.on('update', function (values, handle) {
            document.getElementById('slider-range-value1').innerHTML = values[0];
            document.getElementById('slider-range-value2').innerHTML = values[1];
            document.getElementById('id_age_0').value = values[0];
            document.getElementById('id_age_1').value = values[1];
        });
    }
}

// Maid Card

const maidProfileUrlGen = (id) => {
    const maidProfileUrl = `/maids/view/${id}/profile/`
    return location.origin + maidProfileUrl
}

const maidDetialUrlGen = (id) => {
    const maidDetailUrl = `/maids/view/${id}/`
    return location.origin + maidDetailUrl
}

const tippy_initialisation = function () {
    contentGenerator = (salary, days_off, employment_history) => {
        loaded_content = `<div id="maid-profile-card">
                <div class="container">
                    <div class="row">
                        <div class="col px-2 px-md-3 px-lg-4 mt-4">
                            <div class="row">
                                <div class="col">
                                    <h6 class="text-muted">Salary</h6>
                                    <p>$${salary}</p>
                                </div>
                                <div class="col">
                                    <h6 class="text-muted">Days off</h6>
                                    <p>${days_off}</p>
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <h6 class="text-muted">Employment History</h6>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row">
                        <div class="col px-2 px-md-3">
                            <div class="card custom-card">
                                <p class="lead mb-1">01/02/12 - 01/02/14</p>
                                <h6 class="text-muted mb-0">2 years</h6>
                            </div>
                        </div>
                    </div>
                </div>
            </div>`
        contentString = `<div id='maid-profile-card'>`
        if (salary) {
            contentString += `<p>Salary: $${salary}</p>`
        }
        if (days_off) {
            contentString += `<p>Number of days off: ${days_off}</p>`
        }
        if (employment_history) {
            contentString += '<h5>Employment History</h5><ul>'
            for (eh in employment_history) {
                contentString += `Start Date: ${eh.start_date} End Date:${eh.end_date} Country:${eh.country} Work_duration:${eh.work_duration}`
            }
            contentString += '</ul>'
        }
        return loaded_content
    }
    const loading_content = null;
    let csrftoken = Cookies.get('csrftoken');
    tippy('.maid-card', {
        content: loading_content,
        placement: 'right',
        allowHTML: true,
        theme: 'light',
        onCreate(instance) {
            // Setup our own custom state properties
            instance._isFetching = false;
            instance._data = null;
            instance._error = null;
        },
        onShow(instance) {
            let backend_uri = maidProfileUrlGen(instance.reference.attributes['data-maid'].value);
            console.log(backend_uri)
            if (instance._isFetching || instance._data || instance._error) {
                return;
            }
            instance._isFetching = true;

            fetch(backend_uri, {
                method: 'POST',
                mode: 'same-origin',
                headers: { 'X-CSRFToken': csrftoken }
            })
                .then((response) => response.json())
                .then((result) => {
                    instance._data = contentGenerator(result.salary, result.days_off, result.employment_history);
                    instance.setContent(instance._data);
                })
                .catch((error) => {
                    instance._error = error;
                    console.log(error)
                    instance.setContent(`Request failed. ${error}`);
                })
                .finally(() => {
                    instance._isFetching = false;
                });
        },
        onHidden(instance) {
            instance.setContent(loading_content);
            // Unset these properties so new network requests can be initiated
            instance._data = null;
            instance._error = null;
        }
    })
}

const maidProfileRedirect = (pk) => {
    location.replace(maidDetialUrlGen(pk));
}

// Featured Maids
const displayEmptyContent = function() {
    let featuredMaidsContent = `<div class="row">
                <div class="col text-center">
                    <h1>No Featured Maids</h1>
                </div>
            </div>`;
    $('#featured-maids-wrapper').html(featuredMaidsContent);
}

const displayContent = function(res) {
    let featuredMaidsContent = `<div class="maid-carousel">`;
    for (let index = 0; index < res.data.featured_maids.length; index++) {
        let maid = res.data.featured_maids[index];
        let url_mask = `{% url 'add_to_shortlist' 1 %}`.replace('1', maid.pk);
        featuredMaidsContent += `
                <div class="card maid-card" id='maid-${maid.pk}' data-maid='${maid.pk}'>
                    <div onclick="maidProfileRedirect(${maid.pk})">
                        <img src="${maid.photo_url}" class="card-img-top" alt="Maid Photo">
                        <div class="card-body">
                            <h5 class="card-title">${maid.name}</h5>
                            <p class="card-text">${maid.country_of_origin}</p>
                            <p class="card-text">${maid.age} years old</p>
                            <p class="card-text">${maid.marital_status}</p>
                            <p class="card-text">${maid.type}</p>
                        </div>
                    </div>
                    <div class="card-footer">
                        <a href="${url_mask}" class="btn btn-primary w-100">Add to Shortlist</a>
                    </div>
                </div>`
    };
    featuredMaidsContent += `</div>`;
    $('#featured-maids-wrapper').html(featuredMaidsContent);
    $('.maid-carousel').slick({
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 5,
        slidesToScroll: 5,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 4,
                    slidesToScroll: 4,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
        ]
    });
}

function populateFeaturedMaids(nationality='ANY') {
    let csrftoken = Cookies.get('csrftoken');
    console.log(csrftoken);
    axios({
        method: 'post',
        mode: 'same-origin',
        headers: { 'X-CSRFToken': csrftoken },
        url: '/maids/view/featured/',
        data: {
            'nationality': nationality
        }
    }).then(function (res) {
        if (res.data.count == 0) {
            displayEmptyContent();
        } else {
            displayContent(res);
        }
    })
}

// Maid Carousel
const maidCarousel = function(){
    $('.maid-carousel').slick({
        dots: true,
        infinite: false,
        speed: 300,
        slidesToShow: 4,
        slidesToScroll: 4,
        responsive: [
            {
                breakpoint: 1024,
                settings: {
                    slidesToShow: 3,
                    slidesToScroll: 3,
                    infinite: true,
                    dots: true
                }
            },
            {
                breakpoint: 600,
                settings: {
                    slidesToShow: 2,
                    slidesToScroll: 2
                }
            },
            {
                breakpoint: 480,
                settings: {
                    slidesToShow: 1,
                    slidesToScroll: 1
                }
            }
            // You can unslick at a given breakpoint now by adding:
            // settings: "unslick"
            // instead of a settings object
        ]
    });
}

const maidApititudeWidthMap = {
    '1': '20',
    '2': '40',
    '3': '60',
    '4': '80',
    '5': '100'
}

const assessmentProgressBarInitialisation = function(){
    $('.assessment-progress-bar').each(function () {
        let width_value = $(this).data('value');
        $(this).css('width', maidApititudeWidthMap[width_value] + '%');
    });
}

// Dashboard Agency Plans
const dashboardAgencyPlanChangePlan = function() {
    plan_name = document.getElementById("plansFormControlSelect").value;
    $('.tab-pane').removeClass('active');
    $(`#${plan_name}`).tab('show');
}

const dashboardAgencyPlanAddToCart = function(){
    $('.cart-button').click(function () {
        let priceId = document.querySelector(`input[name="${String($(this).attr('id')).split('btn')[0]}"]:checked`).value;
        location.replace(location.origin.concat(`/payment/cart/add/${priceId}`))
    })
}

// Maid Create Form

const maidCreateFormFunc = function(){
    $(`
            #id_cfi_other_remarks, 
            #id_cfe_other_remarks, 
            #id_cfd_other_remarks,
            #id_geh_other_remarks,
            #id_cok_other_remarks
        `).prop('disabled', true);
    $(`
            #id_cfi_remarks, 
            #id_cfe_remarks, 
            #id_cfd_remarks,
            #id_geh_remarks,
            #id_cok_remarks
        `).on('change', function () {
        let care_type = $(this).prop('id').split('_')[1];
        let selector_text = '#id_' + care_type + '_other_remarks'
        if ($(this).val() == 'OTH') {
            $(selector_text).prop('disabled', false);
        } else {
            $(selector_text).val('')
            $(selector_text).prop('disabled', true)
        }
    });
}

$(function () {
    maidCarousel();
    assessmentProgressBarInitialisation();
    maidCreateFormFunc();
    rangeSliderInitialisation();
    tippy_initialisation();
    populateFeaturedMaids();
    MO(
        {
            "nodeName": document.getElementById('featured-maids-wrapper'),
            "settings": {
                attributes: true,
                childList: true,
                subtree: false
            }
        },
        tippy_initialisation
    );
    // $('#nationalitySelect').on('change', function () {
    //     let nationality = $(this).val();
    //     populateFeaturedMaids(nationality);
    // })
});