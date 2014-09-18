<?php

// Maintenance mode
$maint_mode = 0;
if ($maint_mode) {
    print($maint_message);
    exit();
}

function GetLanguage()
{
    $lang = preg_split('/,/', $_SERVER['HTTP_ACCEPT_LANGUAGE']);
    $lang = preg_split('/-/', $lang[0]);
    $lang = $lang[0];
    return $lang;
}

function GetLocaleFile($lang=NULL)
{
    if (!$lang)
        $lang = GetLanguage();
    $locale_file = "locale/" . $lang;
    if (!file_exists($locale_file))
    {
        // If locale file isn't located default to English
        return 'locale/en';
    }
    return $locale_file;
}

function GetCurrentVersion()
{
    $version_file = fopen('current.txt', 'r');
    $v = fgets($version_file);
    fclose($version_file);
    return $v;
}

// Site update date
$uday = "18";
$umonth = "9";
$uyear = "2014";

// Get current version
$version_current = GetCurrentVersion();

// Get the language settings
if ($_REQUEST['lang'])
{
    $lang = $_REQUEST['lang'];
    $lang_override_h = "/?lang=$lang";
    $lang_override = "&lang=$lang";
}
else
{
    $lang = GetLanguage();
}

// Import global functions & variables
include_once 'globals';

// Get the translated page
include_once GetLocaleFile($lang);

// Small text for menus in Japanese
/*if ($lang == 'ja')
{
    $small1 = '<small>';
    $small2 = '</small>';
}*/

// Right-to-left languages
$rtol_langs = array(1 => 'ar', 'he', 'ur', 'syc', 'syr');
$rtol = array_search($lang, $rtol_langs);
$menu_bg1 = 'res/decor/menu-left.png';
$menu_bg2 = 'res/decor/menu-right.png';
if ($rtol)
{
    $pagedir = ' dir=rtl';
    $menu_bg1 = 'res/decor/menu-right.png';
    $menu_bg2 = 'res/decor/menu-left.png';
}

include 'page/menu';
include 'page/links';
include 'page/home';
include 'page/screenshots';
include 'page/usage';
include 'page/download';
include 'page/translate';
include 'page/credits';

// Create header
print("<html lang=$lang$pagedir>
<head>
<meta charset=UTF-8>
<meta http-equiv=Content-type content=text/html;charset=UTF-8>
<meta name=keywords content=\"debreate, debcreate, deb, .deb, linux, debian, ubuntu, mint, debianize, debianizing, debianizer, pack, package, packager, packaging, pkg, build, builder, building, create, creator, creating, install, installer, installing, dpkg, python, wx, wxpython, wxwidgets, wxwindows, ubucompilator, packin, debipack, giftwrap, debianpackagemaker, debianpackagemakergui, pkgcreator, gui, manager, manage, management, gpl, lgpl, free, open, source, freedom, software, distribution, system, artwork, media, theme, themes, program, programs, programming, script, scripts, scripting, executable, executables, exe, execute\">
<meta name=description content=\"Debreate is a Debian packaging utility designed to aid in packaging software, artwork, media, themes, etc.\">
<meta name=\"wot-verification\" content=\"b4d5556f806bb166b780\"/>

<link rel='shortcut icon' href=res/logo/debreate32.png />

<title>$title_plain</title>

<!-- freehitcでbれあて。sf。ねtounter.net code start -->
<script language=JavaScript type=text/javascript src=http://www.freehitcounter.net/pphlogger2.php?id=debreate></script>
<noscript><img alt='' src=http://www.freehitcounter.net/pphlogger.php?id=debreate&amp;st=img></noscript>
<!-- freehitcounter.net code end -->

<!-- Link to the StyleSheet -->
<link REL=StyleSheet HREF=style.css TYPE=text/css TITLE=Style1 MEDIA=screen>

</head>

<body class='bg-fixed default'>
");

// Create the layout of the page
print("
<table border=0 cellpadding=0 cellspacing=20 width=100%>
  <tr height=100%>
    <td style=vertical-align:top width=0>
      $links
    </td>
    <td style=vertical-align:top width=100% height=100%>
      $menu
    ");

if ($_REQUEST['page'] == 'screenshots')
{
    $current_page = '?page=screenshots';
    print($screenshots);
}

else if ($_REQUEST['page'] == 'usage')
{
    $current_page = '?page=usage';
    print($usage);
}

else if ($_REQUEST['page'] == 'download')
{
    $current_page = '?page=download';
    print($download);
}

else if ($_REQUEST['page'] == 'translate')
{
    $current_page = '?page=translate';
    print($translate);
}

else if ($_REQUEST['page'] == 'credits')
{
    $current_page = '?page=credits';
    print($credits);
}

else
{
    print($home);
}

print("
    </td>
  </tr>
</table>

</body>
</html>
");

?>
