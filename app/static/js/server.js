function validURL(str) {
  var pattern = new RegExp('^(https?:\\/\\/)?' + // protocol
    '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|' + // domain name
    '((\\d{1,3}\\.){3}\\d{1,3}))' + // OR ip (v4) address
    '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*' + // port and path
    '(\\?[;&a-z\\d%_.~+=-]*)?' + // query string
    '(\\#[-a-z\\d_]*)?$', 'i'); // fragment locator
  return !!pattern.test(str);
}

let statusMessages = {
  404 : "Long URL not found!",
  403 : "URL Provided is Blacklisted!",
  304 : "Short URL is Invalid",
  300 : "Short URL is already Used",
  500 : "Create Loop has occured! Contact Admin.",
  501 : "Maximum Length of 50 Characters Exceeded in Custom URL!"
}
let statusCodes = [404,403,304,300,500];

let api_key = "4VzBZpEtuk8gthQrqsp4k6AhsvtzfPjT6m2mERuk";
let appurl = "https://api.shortto.com/v3";
let qrAPI = "https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=";

$(document).ready(function () {
  // DELETE ME LATER
  Snackbar.show({
    text: "The site is in Beta Stage. If you face any issues. Please send an email to support@shortto.com",
    backgroundColor: '#cc3300',
    textColor: '#fff',
    showAction: false
  });

  // Ajax request: URL shortening and error handeling
  $(document).on('submit', "form#main-form", function (e) {
    e.preventDefault();
    //Spinner in Shorten Button
    //  $('.shortbtnz').append("<div class='spinner-container-parent'><div class='spinner-container'><div class='spinner'><div class='spinner-left'><div class='spinner-circle'></div></div><div class='spinner-right'><div class='spinner-circle'></div></div></div></div></div>");
    var form = $(this);
    var url = form.find("#long_url");
    if (!url.val() || url.val() == undefined || !validURL(url.val())) {
      Snackbar.show({
        text: lang.error,
        backgroundColor: '#e22e40',
        textColor: '#fff',
        showAction: false
      });
      $('.text-input').addClass('error');
      return;
    }
    let bodyJSON = {};
    if ($('#short_url').val() != "") {
      bodyJSON = {
        "long_url": $('#long_url').val(),
        "short_url": $('#short_url').val(),
        "g-captcha-client-key" : $('#g-captcha-client-key').val()
      };
    } else {
      bodyJSON = {
        "long_url": $('#long_url').val(),
        "g-captcha-client-key" : $('#g-captcha-client-key').val()
      }
    }
    if ($('#long_url').val() == "") {
      Snackbar.show({
        text: "Long URL Not Provided",
        backgroundColor: '#e22e40',
        textColor: '#fff',
        showAction: false
      });
    } else {
      console.log(bodyJSON);
      $.ajax({
        type: "POST",
        crossDomain: true,
        url: appurl + "/shortto-create-url",
        data: JSON.stringify(bodyJSON),
        dataType: "json",
        async: true,
        headers : {
          'X-Api-Key': api_key,
          "Access-Control-Allow-Origin" : "*", // Required for CORS support to work
          "Access-Control-Allow-Credentials" : true, // Required for cookies, authorization headers with HTTPS 
          'Content-Type':'application/json',
          "accept": "application/json",
        },
        beforeSend: function () {
          $('.shortbtnz').append("<div class='spinner-container-parent' id='spinner-remove'><div class='spinner-container'><div class='spinner'><div class='spinner-left'><div class='spinner-circle'></div></div><div class='spinner-right'><div class='spinner-circle'></div></div></div></div></div>");
        },
        complete: function (xhr, textStatus) {
          grecaptcha.execute('6LdMyawUAAAAAL5rvA7qwC-5F2MfrXy0G2GwgWXU', {action: '/'}).then(function(token) {
            $('#g-captcha-client-key').val(token);
          });
          $('.shortbtnz').find('#spinner-remove').fadeOut("fast");
          $('#spinner-remove').remove();
          console.log(xhr.status);
          if(parseInt(xhr.status) == 500 || parseInt(xhr.status) == 501){
            Snackbar.show({
              text: statusMessages[parseInt(xhr.status)],
              backgroundColor: '#cc3300',
              textColor: '#fff',
              showAction: false
            });
          }
          else if(statusCodes.includes(parseInt(xhr.status))){
            Snackbar.show({
              text: statusMessages[parseInt(xhr.status)],
              backgroundColor: '#edb126',
              textColor: '#fff',
              showAction: false
            });
          }
          else if(parseInt(xhr.status) != 200){
            Snackbar.show({
              text: "Some Error Occured. Please try again!",
              backgroundColor: '#edb126',
              textColor: '#fff',
              showAction: false
            });
          }
        },
        success: function (data) {
          $('.shortbtnz').find('#spinner-remove').fadeOut("fast");
          $('#spinner-remove').remove();
          console.log(data);
          // Snackbar.show({
          //   text: "URL Created!",
          //   backgroundColor: '#e22e40',
          //   textColor: '#fff',
          //   showAction: false
          // });
          if (data.error) {
            Snackbar.show({
              text: "Error Creating URL!",
              backgroundColor: '#e22e40',
              textColor: '#fff',
              showAction: false
            });
            $('.text-input').addClass('error');
          } else {
            $('.text-input').removeClass('error');
            $('.main-advanced').fadeOut('slow');
            if (data.body) {
              var short = data.body;
              Snackbar.show({
                text: lang.success,
                backgroundColor: '#1aa82c',
                textColor: '#fff',
                showAction: false
              });
              $('.modal-contentlink').html('<div class="panel-body"><div class="copy-link-block"><span class="short-url">' + data.body + '</span><button class="btn btn-primary" id="copyurlmodal" type="button"><i class="zmdi zmdi-copy"></i></button></div><div class="qr"><img src="' + qrAPI + data.body + '" alt=""><a href="' + data.body + '" target="_blank" class="mdbtn btn btn-primary copy" data-value="' + data.body + '">' + lang.qr + '</a></div><hr><div class="share-message"><p>' + lang.share + '</p><div class="share"><a href="http://www.facebook.com/sharer.php?u=' + data.body + '" target="_blank" class="btn btn-facebook u_share" title="Facebook"><i class="zmdi zmdi-facebook"></i></a><a href="https://twitter.com/share?url=' + data.body + '" target="_blank" class="btn btn-twitter u_share" title="Twitter"><i class="zmdi zmdi-twitter"></i></a><a href="https://plus.google.com/share?url=' + data.body + '" target="_blank" class="btn btn-danger u_share" title="Google Plus"><i class="zmdi zmdi-google-plus"></i></a><a href="https://www.linkedin.com/shareArticle?mini=true&url=' + data.body + '" target="_blank" class="btn btn-linkedin u_share" title="LinkedIn"><i class="zmdi zmdi-linkedin"></i></a><a href="https://pinterest.com/pin/create/button/?url=' + data.body + '" target="_blank" class="btn btn-pinterest u_share" title="Pinterest"><i class="zmdi zmdi-pinterest"></i></a></div></div></div>');
              $('.overlaylink').fadeIn();
              zClipload();
            } else {
              $('.share-this').slideUp();
              Snackbar.show({
                text: lang.success,
                backgroundColor: '#1aa82c',
                textColor: '#fff',
                showAction: false
              });
            }
            $('.main-advanced').find('input').val('');
            $('.text-input').val('');
            var copy = new Clipboard('#copyurl');
            var copymodal = new Clipboard('#copyurlmodal');
            $("#submit").hide();
            $("#copyurl").attr("data-clipboard-text", data.body).show();
            $("#copyurlmodal").attr("data-clipboard-text",data.body).show();
            copy.on('success', function (e) {
              Snackbar.show({
                text: lang.copy
              });
              $("#copyurl").hide();
              $("#shortenurl").show();
              $('input.text-input').val('');
            });
            copymodal.on('success', function (e) {
              Snackbar.show({
                text: lang.copy
              });
            });
          }
        }
        
      });
    }
  });
  /**
   * Search for URls
   **/
  $("#search").submit(function (e) {
    e.preventDefault();
    var val = $(this).find("input[type=text]").val();
    var action = $(this).attr("action");
    if (val.length > 3) {
      $.ajax({
        type: "POST",
        url: action,
        data: "q=" + val + "&token=" + token,
        beforeSend: function () {
          $(".postprogress").fadeIn();
        },
        complete: function () {
          $('.postprogress').fadeOut();
        },
        success: function (r) {
          $(".return-ajax tbody").html(r);
          $(".url-container").slideUp('fast');
          $(".return-ajax").slideDown('fast');
          loadall();
        }
      });
    } else {
      Snackbar.show({
        text: 'Keyword must be more than 3 characters!'
      });
    }
  });
  /**
   * Server Requests
   **/
  $(document).on('click', '.ajax_call', function (p) {
    p.preventDefault();
    var e = $(this);
    var id = $(this).attr("data-id");
    var action = $(this).attr("data-action");
    var loading = "<img class='loader' src='" + appurl + "/static/loader.gif' style='margin:5px 50%;border:0;' />";
    var title = e.attr("data-title");
    if (typeof ($(this).attr("data-container")) == "undefined") {
      if (typeof ($(this).attr("data-class")) != "undefined") {
        var container = $("." + $(this).attr("data-class"));
        var loading = "<span><i class='glyphicon glyphicon-refresh'></i> Loading</span>";
      } else {
        if (typeof (title) == "undefined") title = "User Account";
        $(this).modal({
          title: title,
          content: "Please wait while loading...",
          confimation: 1
        });
        var container = $("#modal-alert > p");
      }
    } else {
      var container = $("#" + $(this).attr("data-container"));
    }
    var title = $(this).attr("data-title");
    $.ajax({
      type: "POST",
      url: appurl + "/server",
      data: "request=" + action + "&id=" + id + "&token=" + token,
      beforeSend: function () {
        container.html(loading);
      },
      complete: function () {
        loadall();
        $('img.loader').fadeOut("fast");
      },
      success: function (html) {
        if (typeof (e.attr("data-active")) !== "undefined") {
          e.parents("div#user-content").find(".active").removeClass("active");
          e.addClass(e.attr("data-active"));
        }
        container.hide();
        container.html(html);
        container.fadeIn('fast');
      }
    });
  });
  if ($("#widget_activities").length > 0) {
    var intval = $("#widget_activities").attr("data-refresh");
    setInterval(function () {
      server("activities");
    }, intval);
  }
});
/**
 * Realtime Data
 **/
function server(fn) {
  if (fn == "activities") {
    var li = $("#widget_activities").find("li");
    var text = $("#widget_activities h3 small").text();
    var id = li.attr("data-id");
    if (typeof (id) == "undefined") id = 0;
    $.ajax({
      type: "POST",
      url: appurl + "/server",
      data: "request=activities&id=" + id + "&token=" + token,
      beforeSend: function () {
        li.removeClass("new_item");
        $("#widget_activities h3 small").html("<img class='loader' src='" + appurl + "/static/loader.gif' style='margin:0 45%;border:0;' />");
      },
      complete: function () {
        $("#widget_activities h3 small").text(text);
      },
      success: function (r) {
        $("#widget_activities ul").html(r);
      }
    });
  }
  return false;
}