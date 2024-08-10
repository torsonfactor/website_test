
    function WishList(class_name_wishList) {
        var x = document.getElementsByClassName(class_name_wishList);
        var i;
        for (i = 0; i <= x.length; i++) {
            x[i].style.opacity = "7";
        }

    }

    function WishListBack(class_name_wishList) {
        var x = document.getElementsByClassName(class_name_wishList);
        var i;
        for (i = 0; i <= x.length; i++) {
            x[i].style.opacity = "0";
        }
    }

    function WishListDiscounted(class_name_wishList) {
        var x = document.getElementsByClassName(class_name_wishList);
        var i;
        for (i = 0; i <= x.length; i++) {
            x[i].style.opacity = "7";
        }
    }

    function WishListBackDiscounted(class_name_wishList) {
        var x = document.getElementsByClassName(class_name_wishList);
        var i;
        for (i = 0; i <= x.length; i++) {
            x[i].style.opacity = "0";
        }
    }

