========================================
Building MARS environment and Converting 
========================================

For this tutorial, we will use : 

.. topic:: Datas 

    PlantB : Floral bud ( acquisition confocal microscope, datas acquiered at ENS-Lyon)
    
    time course : 0h 
    
Copy datas to your work directory. ::
    
    mkdir mars
    cd mars
    cp $VTISSUEPATH/datas/* .

We have to convert LSM image to a optimized images named Inrimage.
 
For that run Python module : ::

    cp $VTISSUEPATH/python/* .
    python lsm2inr.py

If you have TIFF images, follow this `tutorial <convert_tiff.html>`_


You can observe the resulted images with "zviewer": ::

    zviewer tot1Sub.inr.gz tot2Sub.inr.gz tot3Sub.inr.gz


The binary named "CONSTRUIRE_ARBORESCENCE_ET_SCRIPTS_POUR_RECALAGE" is used to generate groups of shell scripts and work folders.

Run: ::

    CONSTRUIRE_ARBORESCENCE_ET_SCRIPTS_POUR_RECALAGE 1


The MARS work environment is build as follow ::

   ./
       MetaInfo    
           0_Donnees_Initiales/
               	Stack_1/
                Stack_2/
                Stack_3/		
           
           1_Exporte_Empile/
                ./Script_0_Empiler
       
           2_Recalage
                Recalage_0_Manuel/
                Recalage_1_Rigide/
                Recalage_2_Dense/
                ./ScriptSubBaladin
                ./ScriptSubBaloo
                ./ScriptVisuRecalageDense
                ./ScriptVisuRecalageManuel
                ./ScriptVisuRecalageRigide
                ./Script_1_Preparation_Recalage
                ./Script_2_Appariements_Manuels
                ./Script_3_Recalage_Rigide_Manuel
                ./Script_4_5_6_en_local
                ./Script_4_Recalage_Rigide_Auto_sur_grille_0
                ./Script_5_Recalage_Rigide_Auto_sur_grille_1
                ./Script_6_Recalage_Rigide_Auto_sur_grille_2
                ./Script_7_Recalage_Dense_Auto_local_0
                ./Script_8_Recalage_Dense_Auto_local_1
                ./Script_9_Recalage_Dense_Auto_local_2
                ./Script_7_Recalage_Dense_Auto_sur_grille_0
                ./Script_8_Recalage_Dense_Auto_sur_grille_1
                ./Script_9_Recalage_Dense_Auto_sur_grille_2

            3_Fusion/
                ./Script_10_Reech_Et_Fusion 
            
            4_Segmentation/
            
            5_Segmentation_Expert/

