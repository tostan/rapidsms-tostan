$(function (){
	if $("span").length ()> 0 {
		//Il y'a un ou plusieurs elemens  span dans le document 
	}
	else 
	if ($("span").length ()){
		//Ou plus simplement , si il y'a plusieurs elements dans le document 
		
	}
	//Remplace la balise <a> par <em>ca va</em>
	//Remplace la balise <h>  par le premier elements avec la classe titre
	$("a").replaceWith ("<em>ca va </em>");
	$("a").replaceWith ($("titre:first"));
	
	//Replcace tous les <a></a> par <b></b>
	$("b").replaceAll ("h1");
	$("nonose").appendTo ("chien");
	//nonose va remplacer chien
	$("#nonose").replaceAll ("#chien");
	//Nonose va remplacer chien
	$("#chien").replacewith ("#nonose");
	//
	
})
}