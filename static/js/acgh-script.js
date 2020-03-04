let size = 130,
    newsContent = $('.news-content');

newsContent.each(
    function(el) {
        if ($(this).text().length > size) {
            let newText = $(this).text().slice(0, size) + " ...";
            $(this).text(newText);
        }
    }
);


$(document).on('click', '#sendQuestion', function() {

    var order = $("#acgh-order-form").serializeArray();

    console.log('ORDER', order);
    $("#spinner").show()
    $.post("/accept_order/", order)
        .done(response => {
            console.log("success", response)
            $('.border').each(function() {
                $(this).removeClass('border border-danger');
              });
            if (response['errors']) {
                for (let key in response['errors']) {
                  console.log(
                    key, ":", response['errors'][key]
                    );
                  let form = $("#acgh-order-form");
                  let element = form.find(`input[name="${key}"], textarea[name="${key}"]`);
                  // element.after(`<small class="text-danger">${response['errors'][key]}</small>`);
                  element.addClass('is-invalid border border-danger');
                  element.after(`<div class="invalid-feedback">${response['errors'][key]}</div>`);
                  if (key == 'captcha') {
                    let captcha_div = $('#order_captcha_check');
                    captcha_div.addClass('border border-danger');
                    captcha_div.css("border-radius", "3px");
                    $('#order_captcha_check').append(
                    `<p class="text text-danger">
                      ${response['errors'][key]}
                    </p>`
                    )}
                }
            } else {
                var modalBody = $('#feedbackModal').find('.modal-body').first();
                modalBody.html(`
                    Ваше сообщение отправлено, ожидайте звонка специалиста
                `);
            }
        })
        .fail(()=>{
            console.log("failure")
        })
        .always(function(){
            $("#spinner").hide();
        })
    // $('#feedbackModal').find('modal-body').html("<p>TEXT</p>");
});