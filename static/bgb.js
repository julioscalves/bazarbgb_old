/*  
 *   Thanks to rmed
 *   https://www.rmedgar.com/blog/dynamic-fields-flask-wtf/
 */

const ID_RE = /(-)_(-)/;

/**
 * Replace the template index of an element (-_-) with the
 * given index.
 */
function replaceTemplateIndex(value, index) {
    return value.replace(ID_RE, '$1'+index+'$2');
}

/**
 * Adjust the indices of form fields when removing items.
 */
function adjustIndices(removedIndex) {
    var $forms = $('.subform');

    $forms.each(function(i) {
        var $form = $(this);
        var index = parseInt($form.data('index'));
        var newIndex = index - 1;

        if (index < removedIndex) {
            // Skip
            return true;
        }

        // This will replace the original index with the new one
        // only if it is found in the format -num-, preventing
        // accidental replacing of fields that may have numbers
        // intheir names.
        var regex = new RegExp('(-)'+index+'(-)');
        var repVal = '$1'+newIndex+'$2';

        // Change ID in form itself
        $form.attr('id', $form.attr('id').replace(index, newIndex));
        $form.data('index', newIndex);

        // Change IDs in form fields
        $form.find('label, input, select, textarea').each(function(j) {
            var $item = $(this);

            if ($item.is('label')) {
                // Update labels
                $item.attr('for', $item.attr('for').replace(regex, repVal));
                return;
            }

            // Update other fields
            $item.attr('id', $item.attr('id').replace(regex, repVal));
            $item.attr('name', $item.attr('name').replace(regex, repVal));
        });
    });
}

/**
 * Remove a form.
 */
function removeForm() {
    var confirmation = confirm("Quer remover este item?")

    if (confirmation == true) {
        var $removedForm = $(this).closest('.subform');
        var removedIndex = parseInt($removedForm.data('index'));

        $removedForm.remove();

        // Update indices
        adjustIndices(removedIndex);
    }
    
}

/**
 * Add a new form.
 */
function addForm() {
    var $templateForm = $('#boardgame-_-form');

    if ($templateForm.length === 0) {
        console.log('[ERROR] Cannot find template');
        return;
    }

    // Get Last index
    var $lastForm = $('.subform').last();

    var newIndex = 0;

    if ($lastForm.length > 0) {
        newIndex = parseInt($lastForm.data('index')) + 1;
    }

    // Maximum of 20 subforms
    if (newIndex >= 20) {
        console.log('[WARNING] Reached maximum number of elements');
        return;
    }

    // Add elements
    var $newForm = $templateForm.clone();

    $newForm.attr('id', replaceTemplateIndex($newForm.attr('id'), newIndex));
    $newForm.data('index', newIndex);

    $newForm.find('label, input, select, textarea').each(function(idx) {
        var $item = $(this);

        if ($item.is('label')) {
            // Update labels
            $item.attr('for', replaceTemplateIndex($item.attr('for'), newIndex));
            return;
        }

        // Update other fields
        $item.attr('id', replaceTemplateIndex($item.attr('id'), newIndex));
        $item.attr('name', replaceTemplateIndex($item.attr('name'), newIndex));
    });

    // Append
    $('#subforms-container').append($newForm);
    $newForm.addClass('subform');
    $newForm.removeClass('is-hidden');

    $newForm.find('.remove').click(removeForm);
}

function copy() {
    const textArea = document.getElementById("tag-area");
    if (navigator.share) {
        navigator.share({text: textArea.value });
    } else {
        textArea.select();
        document.execCommand("copy");
    }
}; 

function toTitleCase(string) {
    var titleCase = string.toLowerCase().split(' ');

    for (var i = 0; i < titleCase.length; i++) {
        titleCase[i] = titleCase[i].charAt(0).toUpperCase() + titleCase[i].substring(1);
    }

    return titleCase.join(' ');
}

$(document).ready(function() {
    $('#add').click(addForm);
    $('.remove').click(removeForm);
    $('body').css('display', 'none');
    $('body').fadeIn(400);

    $("body").on("keyup change", ".detail-area", function() {
        const DESCRIPTION_MAX = 80;
        $(this).parent().parent().find("span").text(DESCRIPTION_MAX - $(this).val().length + " caracteres restantes.");
    });

    $("body").on("keyup change", "#general_details", function() {
        const DESCRIPTION_MAX = 200;
        $("#general_details_chars").text(DESCRIPTION_MAX - $(this).val().length + " caracteres restantes.");
    });

    $(document).on("change click", ".offer-type", function() {
        let selectValue = $(this).val();
        let priceArea = $(this).parent("div").parent("div").find(".price-input").parent();
        let priceInput = $(this).parent("div").parent("div").find(".price-input");
        
        if (selectValue == "Apenas Venda" || selectValue == "Venda ou Troca") {
            priceInput.attr("required", true);
            priceArea.fadeIn(200);

        } else {
            priceInput.removeAttr("required");
            priceArea.fadeOut(200);
        }
    });

    $(document).on("focus", ".bg-autocomplete", function() {
        $(".bg-autocomplete").autocomplete({
            delay: 300,
            source:function(request, response) {
                $.getJSON("/bgsearch",{ 
                    bgquery: request.term,
                }, function(data) {
                    response(data.bglist);
                });
            },
            minLength: 3,
        });
    })

    $(document).on("focus", "#city", function() {
        var url = 'https://gist.githubusercontent.com/letanure/3012978/raw/2e43be5f86eef95b915c1c804ccc86dc9790a50a/estados-cidades.json';
        var state = $("#states").val();
  
      $("#city").autocomplete({
        delay: 250,
          source: function(request, response) {
              $.getJSON(url, { 
                  bgquery: request.term,
              }, function(data) {
                typing = toTitleCase($("#city").val());
                console.log(typing);
  
                const citiesState = data.estados.filter(function(item) {
                  if (item.sigla == state) {
                    return item.cidades;
                  }
                })
  
                let cities = citiesState[0].cidades.filter(function(city) {
                  return city.startsWith(typing);
                })
  
                response(cities);
              });
          },
          minLength: 2,
      });
  })
});
