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


$('#sendQuestion').click(function() {
    $('.form-feedback').hide();
    $('.confirmation-sending').show();
});