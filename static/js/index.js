// General Redirect Function
const redirect = (url) => {
    window.location.href = toString(url)
}

// Mutation Observer Function
const MO = (node_settings, callback_function, needMutations) => {
    MutationObserver = window.MutationObserver || window.WebKitMutationObserver;

    var observer = new MutationObserver(function (mutations, observer) {
        if (needMutations) {
            callback_function(mutations);
        } else {
            callback_function();
        }
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
        const queryString = window.location.search;
        const urlParams = new URLSearchParams(queryString);
        const ageMin = Number(urlParams.get('age_min'));
        const ageMax = Number(urlParams.get('age_max'));
        const rangeMin = 23;
        const rangeMax = 60;
        const rangeSliderSetting = {
            start: [ageMin ? ageMin : rangeMin, ageMax ? ageMax : rangeMax],
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

const maidDetailUrlGen = (id) => {
    const maidDetailUrl = `/maids/view/${id}/`
    return location.origin + maidDetailUrl
}

const maidProfileRedirect = (pk) => {
    location.replace(maidDetailUrlGen(pk));
}

// Featured Maids
const displayEmptyContent = function() {
    let featuredMaidsContent = `<div class="row">
                <div class="col text-center">
                    <h1 class="fs-12">No Featured Maids</h1>
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
            <a class="text-decoration-none" href="{% url 'maid_detail' ${maid.pk} %}">
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
                </div>
            </a>`
    };
    featuredMaidsContent += `</div>`;
    $('#featured-maids-wrapper').html(featuredMaidsContent);
    maidCarousel();
}

function populateFeaturedMaids(nationality='ANY') {
    let csrftoken = Cookies.get('csrftoken');
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
    AOS.init();
    maidCarousel();
    assessmentProgressBarInitialisation();
    maidCreateFormFunc();
    rangeSliderInitialisation();
    populateFeaturedMaids();
    MO(
        {
            "nodeName": document.getElementById('featured-maids-wrapper'),
            "settings": {
                attributes: true,
                childList: true,
                subtree: false
            }
        }
    );
    $('#nationalitySelect').on('change', function () {
        let nationality = $(this).val();
        populateFeaturedMaids(nationality);
    })
});

window.onload = () => {
    $(".toast").toast('show');
}