/*
Theme Name: Personite
Description: Bootstrap Portfolio Template
Author: Erilisdesign
Theme URI: https://preview.erilisdesign.com/html/personite/
Author URI: https://themeforest.net/user/erilisdesign
Version: 1.0.0
License: https://themeforest.net/licenses/standard
*/

/*------------------------------------------------------
[Table of contents]

1. Loader
2. Navigation
3. Back to top
4. Layout resize
5. Backgrounds
6. Masonry
7. Lightbox
8. Countdown
9. Subscribe Form
10. Contact Form
11. Bootstrap
12. Typed text
13. Slider
------------------------------------------------------*/

(function($){
  "use strict";

  // Vars
  var $html = $('html'),
    $body = $('body'),
    $siteNavbar = $('.site-navbar'),
    $siteNavbarCollapse = $('.site-navbar #navbarCollapse'),
    $siteNavbarToggler = $('.site-navbar .navbar-toggler-alternative'),
    siteNavbar_base = $siteNavbar.attr('data-navbar-base') ? $siteNavbar.attr('data-navbar-base') : '',
    siteNavbar_toggled = $siteNavbar.attr('data-navbar-toggled') ? $siteNavbar.attr('data-navbar-toggled') : '',
    siteNavbar_scrolled = $siteNavbar.attr('data-navbar-scrolled') ? $siteNavbar.attr('data-navbar-scrolled') : '',
    siteNavbar_expand = 992,
    siteNavbar_dropdownHover = true,
    $btn_backToTop = $('.btn-back-to-top');

  function getWindowWidth(){
    return Math.max($(window).width(), window.innerWidth);
  }

  // [1. Loader]
  window.addEventListener( 'load', function(){
    document.querySelector('body').classList.add('loaded');
  });

  // [2. Navigation]
  function personite_navigation(){

    // Close all submenus when dropdown is hiding
    $('.navbar-nav > .dropdown').on('hide.bs.dropdown', function() {
      var $submenus = $(this).find('.dropdown-submenu');

      $submenus.removeClass('show dropdown-target');
      $submenus.find('.dropdown-menu').removeClass('show');
    });

    // Add hovered class
    $('.navbar-nav > .dropdown').on('shown.bs.dropdown', function() {
      if (window.innerWidth > 991) {
        $(this).addClass('hovered');
      } else {
        $(this).removeClass('hovered');
      }
    });

    // Enable clicks inside dropdown
    $(document).on('click', '.navbar-nav > .dropdown', function(e) {
      e.stopPropagation();
    });

    // Dropdown
    var navbarDropdown = document.querySelectorAll('.navbar-nav > .dropdown, .navbar-nav .dropdown-submenu');

    [].forEach.call(navbarDropdown, function(dropdown) {
      'mouseenter mouseleave click'.split(' ').forEach(function(event) {
        dropdown.addEventListener(event, function(e) {
          if (window.innerWidth >= siteNavbar_expand && siteNavbar_dropdownHover === true ) {
            // Hover

            var _this = this;

            if( event === 'mouseenter' ){
              if( _this.classList.contains('dropdown') ){
                var toggle = _this.querySelector('[data-toggle="dropdown"]');

                if( _this.classList.contains('show') ){
                  $(toggle).dropdown('hide');
                  $(toggle).blur();
                } else {
                  $(toggle).dropdown('show');

                  e.stopPropagation();
                }
              } else if( _this.classList.contains('dropdown-submenu') ){
                if( $(_this).parent().find('.dropdown-target') ){
                  $(_this).parent().find('.dropdown-target.dropdown-submenu').removeClass('show dropdown-target');
                }

                _this.classList.add('hovered', 'show', 'dropdown-target');
              }
            } else {
              if( _this.classList.contains('dropdown') ){
                var toggle = _this.querySelector('[data-toggle="dropdown"]');

                $(toggle).dropdown('hide');
                $(toggle).blur();
              } else if( _this.classList.contains('dropdown-submenu') ){
                _this.classList.remove('show', 'dropdown-target');
              }
            }
          } else {
            // Click

            if( event === 'click' && e.target.classList.contains('dropdown-toggle') && e.target.parentNode.classList.contains('dropdown-submenu') ){
              if( e.target.parentNode.classList.contains('dropdown') ){
                return true;
              }

              e.stopPropagation();
              e.preventDefault();

              var _this = e.target,
                ddSubmenu = _this.parentNode,
                ddMenu = _this.nextElementSibling;

              if( ddSubmenu.classList.contains('show') ){

                ddSubmenu.classList.remove('show', 'dropdown-target');
                ddMenu.classList.remove('show');

                if( ddMenu.querySelectorAll('.dropdown-target').length > 0 ){
                  var submenuNodeList = ddMenu.querySelectorAll('.dropdown-target.dropdown-submenu'), i;

                  for (i = 0; i < submenuNodeList.length; ++i) {
                    submenuNodeList[i].classList.remove('show', 'dropdown-target');
                    submenuNodeList[i].querySelector('.dropdown-menu').classList.remove('show');
                  }
                }
              } else {
                if( ddSubmenu.parentNode.querySelectorAll('.dropdown-target').length > 0 ){
                  var submenuNodeList = ddSubmenu.parentNode.querySelectorAll('.dropdown-target.dropdown-submenu'), i;

                  for (i = 0; i < submenuNodeList.length; ++i) {
                    submenuNodeList[i].classList.remove('show', 'dropdown-target');
                    submenuNodeList[i].querySelector('.dropdown-menu').classList.remove('show');
                  }
                }

                ddSubmenu.classList.add('hovered', 'show', 'dropdown-target');
                ddMenu.classList.add('show');
              }
            }
          }
        });
      });
    });

    // Navigation collapse
    $siteNavbarCollapse.on( 'show.bs.collapse', function(){
      $siteNavbar.addClass('navbar-toggled-show');
      $siteNavbarToggler.blur();
      personite_navChangeClasses('toggled');
    });

    $siteNavbarCollapse.on( 'hidden.bs.collapse', function(){
      $siteNavbar.removeClass('navbar-toggled-show');
      $siteNavbarToggler.blur();

      if ( $siteNavbar.hasClass('scrolled') ){
        personite_navChangeClasses('scrolled');
      } else {
        personite_navChangeClasses();
      }
    });

    // Clickable Links
    $(document).on( 'click', 'a.scrollto, .site-navbar a[href^="#"]', function(e){
      var target;

      // Make sure this.hash has a value before overriding default behavior
      if ( this.hash !== '' && this.hash !== '#!' && $( this.hash ).length > 0 ){
        target = this.hash;
      } else {
        return false;
      }

      if( target !== '' ){
        // Prevent default anchor click behavior
        e.preventDefault();

        if( $( target ).length > 0 ){
          var targetPosition = parseInt( Math.max( document.querySelector(target).offsetTop, $(target).offset().top ), 10 );

          $(window).scrollTo(targetPosition,800);

          $(this).blur();
        }
      }

      return false;
    });

    // Back to top
    $(document).on( 'click', '.btn-back-to-top', function(e){
      e.preventDefault();

      $(window).scrollTo(0,800);

      $(this).blur();
    });

    // Close nav on click outside of '.sitenav-collapse-inner'
    $(document).on( 'click touchstart', function(e){
      if ( $siteNavbar.is(e.target) || $(e.target).closest('.site-navbar').hasClass('site-navbar') || $(e.target).hasClass('navbar-toggler') || $(e.target).hasClass('navbar-toggler-alternative') ){
        return;
      }

      if ( $siteNavbarToggler.attr('aria-expanded') === 'true' ){
        $siteNavbarToggler.trigger('click');
      }
    });

  }

  function personite_navOnScroll(){
    if ( $siteNavbar.length > 0 ){
      var currentPos = $(window).scrollTop();

      if ( currentPos > 0 ){
        if ( $siteNavbar.hasClass('scrolled') ){
          return;
        }

        $siteNavbar.addClass('scrolled').removeClass('scrolled-0');

        if( $siteNavbar.hasClass('navbar-toggled-show') ){
          personite_navChangeClasses('toggled');
        } else {
          personite_navChangeClasses('scrolled');
        }
      } else {
        $siteNavbar.removeClass('scrolled').addClass('scrolled-0');

        if( $siteNavbar.hasClass('navbar-toggled-show') ){
          personite_navChangeClasses('toggled');
        } else if( $body.hasClass('flyer-open') ){
          personite_navChangeClasses('flyer');
        } else {
          personite_navChangeClasses();
        }
      }
    }
  }

  var nav_event_old;
  function personite_navChangeClasses(nav_event){
    if( nav_event_old === nav_event && !( nav_event == '' || nav_event == undefined ) )
      return;

    if( nav_event === 'toggled' && siteNavbar_toggled ){
      $siteNavbar.removeClass('navbar-light navbar-dark', siteNavbar_base, siteNavbar_scrolled);
      $siteNavbar.addClass(siteNavbar_toggled);
    } else if( nav_event === 'scrolled' && siteNavbar_scrolled ){
      $siteNavbar.removeClass('navbar-light navbar-dark', siteNavbar_base, siteNavbar_toggled);
      $siteNavbar.addClass(siteNavbar_scrolled);
    } else {
      if(siteNavbar_base){
        $siteNavbar.removeClass('navbar-light navbar-dark', siteNavbar_toggled, siteNavbar_scrolled);
        $siteNavbar.addClass(siteNavbar_base);
      }
    }

    if( $siteNavbar.hasClass('navbar-light') ){
      $('[data-on-navbar-light]').each(function(){
        var el = $(this);

        if( el.attr('data-on-navbar-dark') ){
          el.removeClass(el.attr('data-on-navbar-dark'));
        }
        if( el.attr('data-on-navbar-light') ){
          el.addClass(el.attr('data-on-navbar-light'));
        }
      });
    } else if( $siteNavbar.hasClass('navbar-dark') ){
      $('[data-on-navbar-dark]').each(function(){
        var el = $(this);

        if( el.attr('data-on-navbar-light') ){
          el.removeClass(el.attr('data-on-navbar-light'));
        }
        if( el.attr('data-on-navbar-dark') ){
          el.addClass(el.attr('data-on-navbar-dark'));
        }
      });
    }

    nav_event_old = nav_event;
  }

  // [3. Back to top]
  function personite_backToTop(){
    if( $btn_backToTop.length > 0 ){
      var currentPos = $(window).scrollTop();

      if( currentPos > 400 ){
        $btn_backToTop.addClass('show');
      } else {
        $btn_backToTop.removeClass('show');
      }
    }
  }

  // [4. Layout Resize]
  function personite_layoutResize(){
    if( getWindowWidth() >= 1200 ){
      if ( $siteNavbarToggler.attr('aria-expanded') === 'true' ){
        $siteNavbar.removeClass('navbar-toggled-show');
        $siteNavbarCollapse.removeClass('show');
        $siteNavbarToggler.attr('aria-expanded','false');
        $siteNavbarToggler.addClass('collapsed');
        personite_navChangeClasses();
      }
    }
  }

  // [5. Backgrounds]
  function personite_backgrounds(){

    // Image
    var $bgImage = $('.bg-image-holder');
    if($bgImage.length){
      $bgImage.each(function(){
        var $self = $(this);
        var src = $self.children('img').attr('src');

        $self.css('background-image','url('+src+')').children('img').hide();
      });
    }

    // Video Background
    if ( $body.hasClass('mobile') ){
      $('.video-wrapper').css('display','none');
    }

  }

  // [6. Masonry]
  function personite_masonryLayout(){
    if ($('.masonry-container').length > 0) {
      var $masonryContainer = $('.masonry-container'),
        $columnWidth = $masonryContainer.data('column-width');

      if($columnWidth == null){
        var $columnWidth = '.masonry-item';
      }

      $masonryContainer.isotope({
        filter: '*',
        animationEngine: 'best-available',
        resizable: false,
        itemSelector : '.masonry-item',
        masonry: {
          columnWidth: $columnWidth
        },
        animationOptions: {
          duration: 750,
          easing: 'linear',
          queue: false
        }
      });

      // layout Isotope after each image loads
      $masonryContainer.imagesLoaded().progress( function() {
        $masonryContainer.isotope('layout');
      });
    }

    $('nav.masonry-filter a').on('click', function(e) {
      e.preventDefault();

      var selector = $(this).attr('data-filter');
      $masonryContainer.isotope({ filter: selector });
      $('nav.masonry-filter a').removeClass('active');
      $(this).addClass('active');

      return false;
    });
  }

  // [7. Lightbox]
  function personite_lightbox(){
    if(!$().featherlight){
      console.log('Featherlight: featherlight not defined.');
      return true;
    }

    $.extend($.featherlight.defaults, {
      closeIcon: '<i class="fas fa-times"></i>'
    });

    $.extend($.featherlightGallery.defaults, {
      previousIcon: '<i class="fas fa-chevron-left"></i>',
      nextIcon: '<i class="fas fa-chevron-right"></i>'
    });

    $.featherlight.prototype.afterOpen = function(){
      $body.addClass('featherlight-open');
    };

    $.featherlight.prototype.afterContent = function(){
      var title = this.$currentTarget.attr('data-title');
      var text = this.$currentTarget.attr('data-text');

      if( !title && !text )
        return;

      this.$instance.find('.caption').remove();

      var title = title ? '<h4 class="title-gallery">' + title + '</h4>' : '',
        text = text ? '<p class="text-gallery">' + text + '</p>' : '';

      $('<div class="caption">').html( title + text ).appendTo(this.$instance.find('.featherlight-content'));
    };

    $.featherlight.prototype.afterClose = function(){
      $body.removeClass('featherlight-open');
    };
  }

  // [8. Countdown]
  function personite_countdown(){
    var countdown = $('.countdown[data-countdown]');

    if (countdown.length > 0){
      countdown.each(function(){
        var $countdown = $(this),
          finalDate = $countdown.data('countdown');
        $countdown.countdown(finalDate, function(event){
          $countdown.html(event.strftime(
            '<div class="countdown-container row"> <div class="col-6 col-sm-auto"><div class="countdown-item"><div class="number">%-D</div><span class="title">Day%!d</span></div></div><div class="col-6 col-sm-auto"><div class="countdown-item"><div class="number">%H</div><span class="title">Hours</span></div></div><div class="col-6 col-sm-auto"><div class="countdown-item"><div class="number">%M</div><span class="title">Minutes</span></div></div><div class="col-6 col-sm-auto"><div class="countdown-item"><div class="number">%S</div><span class="title">Seconds</span></div></div></div>'
          ));
        });
      });
    }
  }

  // [9. Subscribe Form]
  function personite_subscribeForm(){
    var $subscribeForm = $('.subscribe-form');

    if ( $subscribeForm.length > 0 ){
      $subscribeForm.each( function(){
        var el = $(this),
          elResult = el.find('.subscribe-form-result');

        el.find('form').validate({
          submitHandler: function(form) {
            elResult.fadeOut( 500 );

            $(form).ajaxSubmit({
              target: elResult,
              dataType: 'json',
              resetForm: true,
              success: function( data ) {
                elResult.html( data.message ).fadeIn( 500 );
                if( data.alert != 'error' ) {
                  $(form).clearForm();
                  setTimeout(function(){
                    elResult.fadeOut( 500 );
                  }, 5000);
                };
              }
            });
          }
        });

      });
    }
  }

  // [10. Contact Form]
  function personite_contactForm(){
    var $contactForm = $('.contact-form');

    if ( $contactForm.length > 0 ){
      $contactForm.each( function(){
        var el = $(this),
          elResult = el.find('.contact-form-result');

        el.find('form').validate({
          submitHandler: function(form) {
            elResult.fadeOut( 500 );

            $(form).ajaxSubmit({
              target: elResult,
              dataType: 'json',
              success: function( data ) {
                elResult.html( data.message ).fadeIn( 500 );
                if( data.alert != 'error' ) {
                  $(form).clearForm();
                  setTimeout(function(){
                    elResult.fadeOut( 500 );
                  }, 5000);
                };
              }
            });
          }
        });

      });
    }
  }

  // [11. Bootstrap]
  function personite_bootstrap(){

    // Botostrap Tootltips
    $('[data-toggle="tooltip"]').tooltip();

    // Bootstrap Popovers
    $('[data-toggle="popover"]').popover();

  }

  // [12. Typed text]
  function personite_typedText(){
    var toggle = document.querySelectorAll('[data-toggle="typed"]');

    function init(el) {
      var elementOptions = el.dataset.options;
          elementOptions = elementOptions ? JSON.parse(elementOptions) : {};
      var defaultOptions = {
        typeSpeed: 40,
        backSpeed: 40,
        backDelay: 3000,
        loop: true
      }
      var options = Object.assign(defaultOptions, elementOptions);

      new Typed(el, options);
    }

    if (typeof Typed !== 'undefined' && toggle) {
      [].forEach.call(toggle, function(el) {
        init(el);
      });
    }

  }

  // [13. Slider]
  function personite_slider() {
    var $slider = $('.slider');

    if($slider.length > 0){

      if( !$slider.hasClass('slick-initialized') ){
		$slider.on('init', function(event, slick){
          websiteSlider_layout();
          websiteSlider_resize();
        });

        $slider.slick({
          slidesToShow: 1,
          infinite: true,
          nextArrow: '<button type="button" class="slick-next"><i class="fas fa-angle-right"></i></button>',
          prevArrow: '<button type="button" class="slick-prev"><i class="fas fa-angle-left"></i></button>'
        });

		$slider.on('reInit swipe setPosition destroy afterChange', function(event, slick){
          websiteSlider_layout();
          websiteSlider_resize();
        });
      }

      if( 1199 >= getWindowWidth() && $slider.hasClass('slick-initialized') && $slider.hasClass('slick-destroy-xl') ){
        $slider.slick('unslick');
      }

      if( 991 >= getWindowWidth() && $slider.hasClass('slick-initialized') && $slider.hasClass('slick-destroy-lg') ){
        $slider.slick('unslick');
      }

      if( 767 >= getWindowWidth() && $slider.hasClass('slick-initialized') && $slider.hasClass('slick-destroy-md') ){
        $slider.slick('unslick');
      }

      if( 575 >= getWindowWidth() && $slider.hasClass('slick-initialized') && $slider.hasClass('slick-destroy-sm') ){
        $slider.slick('unslick');
      }

    }
  }

  $(document).ready(function($){
    personite_navigation();
    personite_navOnScroll();
    personite_backToTop();
    personite_layoutResize();
    personite_backgrounds();
    personite_masonryLayout();
    personite_lightbox();
    personite_countdown();
    personite_subscribeForm();
    personite_contactForm();
    personite_bootstrap();
    personite_typedText();
    personite_slider();
  });

  $(window).on( 'scroll', function(){
    personite_navOnScroll();
    personite_backToTop();
  });

  $(window).on('resize', function(){
    personite_navOnScroll();
    personite_backToTop();
    personite_slider();
  });

})(jQuery);