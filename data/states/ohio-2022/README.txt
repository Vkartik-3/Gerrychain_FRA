Ohio 2022 General Election Precinct-Level Boundaries and Results

## RDH Date Retrieval
09/08/23

## RDH Update Date
09/12/23

## Sources
The RDH retrieved 2022 general election precinct-level results from the Ohio Secretary of State originally (https://www.ohiosos.gov/elections/election-results-and-data/2022-official-election-results/) and used the data hosted on the RDH site for this file (https://redistrictingdatahub.org/dataset/ohio-2022-general-election-precinct-level-results/)
Precinct boundaries were collected by Open Elections and provided to the RDH for processing. 

## Notes on Field Names (adapted from VEST):
Columns reporting votes generally follow the pattern: 
One example is:
G16PREDCLI
The first character is G for a general election, P for a primary, S for a special, and R for a runoff.
Characters 2 and 3 are the year of the election.*
Characters 4-6 represent the office type (see list below).
Character 7 represents the party of the candidate.
Characters 8-10 are the first three letters of the candidate's last name.

*To fit within the GIS 10 character limit for field names, the naming convention is slightly different for the State Legislature and US House of Representatives. All fields are listed below with definitions.

Office Codes Used:
ATG - Attorney General
AUD - Auditor of State
CJU - Chief Justice of the Supreme Court
GOV - Governor and Lieutenant Governor
JUS - Justice of the Supreme Court
TRE - Treasurer of State
SOS - Secretary Of State
USS - U.S. Senate
CON## - U.S. Congress
SL###  - State Legislative Lower
SU##  - State Legislative Upper

## Fields:
Field Name Description
**Across all files**
UNIQUE_ID   Unique ID for each precinct  
VTDST22	    3-digit COUNTYFP + 3-digit Ohio precinct code                                                     
COUNTYFP    County FIP identifier                                                              
COUNTYNM    County Name                                                                        
PRECINCT    Precinct Name 
PRECCODE    3-digit Ohio precinct code  
geometry    geometry   


**oh_2022_gen_prec_st.shp**
G22ATGDCRO Attorney General  Jeffrey A. Crossman (D)                                          
G22ATGRYOS Attorney General  Dave Yost (R)                                                    
G22AUDDSAP Auditor of State  Taylor Sappington (D)                                            
G22AUDRFAB Auditor of State  Keith Faber (R)                                                  
G22CJUDBRU Chief Justice of the Supreme Court Term Commencing 01/01/2023 Jennifer Brunner (D) 
G22CJURKEN Chief Justice of the Supreme Court Term Commencing 01/01/2023 Sharon L. Kennedy (R)
G22GOVDWHA Governor and Lieutenant Governor  Nan Whaley and Cheryl L. Stephens (D)            
G22GOVRDEW Governor and Lieutenant Governor  Mike DeWine and Jon Husted (R)                   
G22JUSDJAM Justice of the Supreme Court Term Commencing 01/01/2023 Terri Jamison (D)          
G22JUSDZAY Justice of the Supreme Court Term Commencing 01/02/2023 Marilyn Zayas (D)          
G22JUSRDEW Justice of the Supreme Court Term Commencing 01/02/2023 Pat DeWine (R)             
G22JUSRFIS Justice of the Supreme Court Term Commencing 01/01/2023 Pat Fischer (R)            
G22SOSDCLA Secretary of State  Chelsea Clark (D)                                              
G22SOSOMAR Secretary of State  Terpsehore Tore Maras                                          
G22SOSRLAR Secretary of State  Frank LaRose (R)                                               
G22TREDSCH Treasurer of State  Scott Schertzer (D)                                            
G22TRERSPR Treasurer of State  Robert Sprague (R)                                             
G22USSDRYA U.S. Senator  Tim Ryan (D)                                                         
G22USSRVAN U.S. Senator  JD Vance (R)   

**oh_2022_gen_prec_cong.shp**                                                      
GCON01DLAN Representative to Congress - District 01  Greg Landsman (D)                        
GCON01RCHA Representative to Congress - District 01  Steve Chabot (R)                         
GCON02DMEA Representative to Congress - District 02  Samantha Meadows (D)                     
GCON02RWEN Representative to Congress - District 02  Brad Wenstrup (R)                        
GCON03DBEA Representative to Congress - District 03  Joyce Beatty (D)                         
GCON03RSTA Representative to Congress - District 03  Lee R. Stahley (R)                       
GCON04DWIL Representative to Congress - District 04  Tamie Wilson (D)                         
GCON04RJOR Representative to Congress - District 04  Jim Jordan (R)                           
GCON05DSWA Representative to Congress - District 05  Craig Swartz (D)                         
GCON05RLAT Representative to Congress - District 05  Bob Latta (R)                            
GCON06DLYR Representative to Congress - District 06  Louis G. Lyras (D)                       
GCON06RJOH Representative to Congress - District 06  Bill Johnson (R)                         
GCON07DDIE Representative to Congress - District 07  Matthew Diemer (D)                       
GCON07RMIL Representative to Congress - District 07  Max Miller (R)                           
GCON08DENO Representative to Congress - District 08  Vanessa Enoch (D)                        
GCON08RDAV Representative to Congress - District 08  Warren Davidson (R)                      
GCON09DKAP Representative to Congress - District 09  Marcy Kaptur (D)                         
GCON09RMAJ Representative to Congress - District 09  J.R. Majewski (R)                        
GCON10DESR Representative to Congress - District 10  David Esrati (D)                         
GCON10RTUR Representative to Congress - District 10  Mike Turner (R)                          
GCON11DBRO Representative to Congress - District 11  Shontel Brown (D)                        
GCON11RBRE Representative to Congress - District 11  Eric J. Brewer (R)                       
GCON12DRIP Representative to Congress - District 12  Amy Rippel-Elton (D)                     
GCON12RBAL Representative to Congress - District 12  Troy Balderson (R)                       
GCON13DSYK Representative to Congress - District 13  Emilia Sykes (D)                         
GCON13RGIL Representative to Congress - District 13  Madison Gesiotto Gilbert (R)             
GCON14DKIL Representative to Congress - District 14  Matt Kilboy (D)                          
GCON14RJOY Representative to Congress - District 14  David P. Joyce (R)                       
GCON15DJOS Representative to Congress - District 15  Gary Josephson (D)                       
GCON15RCAR Representative to Congress - District 15  Mike Carey (R)                           

**ooh_2022_gen_prec_sldl.shp**
GSL001DJAR State Representative - District 01  Dontavius Jarrells (D)                         
GSL002DHUM State Representative - District 02  Latyna M. Humphrey (D)                         
GSL003DMOH State Representative - District 03  Ismail Mohamed (D)                             
GSL003RLAN State Representative - District 03  J. Josiah Lanning (R)                          
GSL004DLIG State Representative - District 04  Mary Lightbody (D)                             
GSL004RRUD State Representative - District 04  Jill Rudler (R)                                
GSL005DBRO State Representative - District 05  Richard Brown (D)                              
GSL005RBEA State Representative - District 05  Ronald Beach IV (R)                            
GSL006DMIL State Representative - District 06  Adam C. Miller (D)                             
GSL006RWHA State Representative - District 06  Joe Wharton (R)                                
GSL007DRUS State Representative - District 07  Allison Russo (D)                              
GSL008DLIS State Representative - District 08  Beth Liston (D)                                
GSL008RTRU State Representative - District 08  Zully Truemper (R)                             
GSL009DABD State Representative - District 09  Munira Yasin Abdullahi (D)                     
GSL010DHAR State Representative - District 10  Russell Harris (D)                             
GSL010RDOB State Representative - District 10  David A.  Dobos (R)                            
GSL011DSOM State Representative - District 11  Anita Somani (D)                               
GSL011RTAR State Representative - District 11  Omar Tarazi (R)                                
GSL012RSTE State Representative - District 12  Brian Stewart (R)                              
GSL013DSKI State Representative - District 13  Michael J. Skindell (D)                        
GSL013RDAV State Representative - District 13  Keith A. Davey (R)                             
GSL014DBRE State Representative - District 14  Sean P. Brennan (D)                            
GSL014RAUS State Representative - District 14  Jolene B. Austin (R)                           
GSL015DDEL State Representative - District 15  Richard Dell'Aquila (D)                        
GSL016DSWE State Representative - District 16  Bride Rose Sweeney (D)                         
GSL016RLAM State Representative - District 16  Michael Lamb (R)                               
GSL017DGRE State Representative - District 17  Troy J. Greenfield (D)                         
GSL017RPAT State Representative - District 17  Thomas F. Patton (R)                           
GSL018DBRE State Representative - District 18  Darnell T. Brewer (D)                          
GSL018RTAY State Representative - District 18  Shalira Taylor (R)                             
GSL019DROB State Representative - District 19  Phil Robinson (D)                              
GSL019RBRO State Representative - District 19  Ron Brough (R)                                 
GSL020DUPC State Representative - District 20  Terrence Upchurch (D)                          
GSL021DFOR State Representative - District 21  Elliot Forhan (D)                              
GSL021RPOW State Representative - District 21  Kelly Powell (R)                               
GSL022DBRE State Representative - District 22  Juanita O. Brent (D)                           
GSL023DTRO State Representative - District 23  Daniel P. Troy (D)                             
GSL023RPHI State Representative - District 23  George M. Phillips (R)                         
GSL024DISA State Representative - District 24  Dani Isaacsohn (D)                             
GSL024RKOE State Representative - District 24  Adam Paul Teague Koehler (R)                   
GSL025DTHO State Representative - District 25  Cecil Thomas (D)                               
GSL025RBRE State Representative - District 25  John Breadon (R)                               
GSL026DDEN State Representative - District 26  Sedrick Denson (D)                             
GSL027DBAK State Representative - District 27  Rachel Baker (D)                               
GSL027RGIR State Representative - District 27  Jenn Giroux (R)                                
GSL028DMIR State Representative - District 28  Jessica E. Miranda (D)                         
GSL028RMON State Representative - District 28  Chris Monzel (R)                               
GSL029RABR State Representative - District 29  Cindy Abrams (R)                               
GSL030DMAY State Representative - District 30  Alissa Mayhaus (D)                             
GSL030RSEI State Representative - District 30  Bill Seitz (R)                                 
GSL031DDAR State Representative - District 31  Rita Darrow (D)                                
GSL031RROE State Representative - District 31  Bill Roemer (R)                                
GSL032DSHA State Representative - District 32  Matt Shaughnessy (D)                           
GSL032RYOU State Representative - District 32  Bob Young (R)                                  
GSL033DGAL State Representative - District 33  Tavia Galonski (D)                             
GSL033RAND State Representative - District 33  Kristopher J. Anderson (R)                     
GSL034DWEI State Representative - District 34  Casey Weinstein (D)                            
GSL034RBIG State Representative - District 34  Beth A. Bigham (R)                             
GSL035DONE State Representative - District 35  Lori O'Neill (D)                               
GSL035RDEM State Representative - District 35  Steve Demetriou (R)                            
GSL036DCAR State Representative - District 36  Addison Caruso (D)                             
GSL036RWHI State Representative - District 36  Andrea White (R)                               
GSL037RYOU State Representative - District 37  Tom Young (R)                                  
GSL038DBLA State Representative - District 38  Willis E. Blackshear Jr (D)                    
GSL039DJAC State Representative - District 39  Leronda F. Jackson (D)                         
GSL039RPLU State Representative - District 39  Phil Plummer (R)                               
GSL040DCOX State Representative - District 40  Amy Cox (D)                                    
GSL040RCRE State Representative - District 40  Rodney Creech (R)                              
GSL041DLAR State Representative - District 41  Nancy Larson (D)                               
GSL041RWIL State Representative - District 41  Josh Williams (R)                              
GSL042DWHI State Representative - District 42  Erika White (D)                                
GSL042RMER State Representative - District 42  Derek Merrin (R)                               
GSL043DGRI State Representative - District 43  Michele Grim (D)                               
GSL043RHEN State Representative - District 43  Wendi Hendricks (R)                            
GSL044DROG State Representative - District 44  Elgin Rogers Jr (D)                            
GSL044RPAL State Representative - District 44  Roy G. Palmer III (R)                          
GSL045DHOR State Representative - District 45  Chuck Horn (D)                                 
GSL045RGRO State Representative - District 45  Jennifer Gross (R)                             
GSL046DMUL State Representative - District 46  Lawrence Mulligan (D)                          
GSL046RHAL State Representative - District 46  Thomas Hall (R)                                
GSL047DLAW State Representative - District 47  Sam Lawrence (D)                               
GSL047RCAR State Representative - District 47  Sara Carruthers (R)                            
GSL048DSMI State Representative - District 48  David Smith (D)                                
GSL048ROEL State Representative - District 48  Scott Oelslager (R)                            
GSL049DWES State Representative - District 49  Thomas E. West (D)                             
GSL049RTHO State Representative - District 49  Jim Thomas (R)                                 
GSL050RSTO State Representative - District 50  Reggie Stoltzfus (R)                           
GSL051RHIL State Representative - District 51  Brett Hudson Hillyer (R)                       
GSL052DPHI State Representative - District 52  Regan L. Phillips (D)                          
GSL052RMAN State Representative - District 52  Gayle Manning (R)                              
GSL053DMIL State Representative - District 53  Joe Miller (D)                                 
GSL053RGAL State Representative - District 53  Marty Gallagher (R)                            
GSL054DBUR State Representative - District 54  Bryan Burgess (D)                              
GSL054RSTE State Representative - District 54  Dick Stein (R)                                 
GSL055DZOR State Representative - District 55  Paul Zorn (D)                                  
GSL055RLIP State Representative - District 55  Scott Lipps (R)                                
GSL056DBEN State Representative - District 56  Joy Bennett (D)                                
GSL056RMAT State Representative - District 56  Adam Mathews (R)                               
GSL057DROS State Representative - District 57  Evan Rosborough (D)                            
GSL057RCAL State Representative - District 57  Jamie Callender (R)                            
GSL058DNEF State Representative - District 58  Wm Bruce Neff (D)                              
GSL058RCUT State Representative - District 58  Al Cutrona (R)                                 
GSL059DMCN State Representative - District 59  Lauren R. McNally (D)                          
GSL059OBEI State Representative - District 59  Greg Beight                                    
GSL059OUNG State Representative - District 59  Eric C. Ungaro                                 
GSL060RJOR State Representative - District 60  Kris Jordan (R)                                
GSL061DVAL State Representative - District 61  Louise Valentine (D)                           
GSL061RLEA State Representative - District 61  Beth Lear (R)                                  
GSL062DFLI State Representative - District 62  Brian Flick (D)                                
GSL062RSCH State Representative - District 62  Jean Schmidt (R)                               
GSL063DPER State Representative - District 63  Richard J. Perry (D)                           
GSL063RBIR State Representative - District 63  Adam C. Bird (R)                               
GSL064DPET State Representative - District 64  Vincent Peterson II (D)                        
GSL064RSAN State Representative - District 64  Nick Santucci (R)                              
GSL065ODON State Representative - District 65  Jennifer Donnelly                              
GSL065RLOY State Representative - District 65  Mike Loychik (R)                               
GSL066DCOL State Representative - District 66  Christina Collins (D)                          
GSL066RRAY State Representative - District 66  Sharon A. Ray (R)                              
GSL067DBUR State Representative - District 67  Drew Burge (D)                                 
GSL067RMIL State Representative - District 67  Melanie Miller (R)                             
GSL068RCLA State Representative - District 68  Thad Claggett (R)                              
GSL069DOWE State Representative - District 69  Charlotte Owens (D)                            
GSL069RMIL State Representative - District 69  Kevin D. Miller (R)                            
GSL070DPRI State Representative - District 70  Eric Price (D)                                 
GSL070RLAM State Representative - District 70  Brian Lampton (R)                              
GSL071DDUF State Representative - District 71  James Harvey Duffee (D)                        
GSL071RDEA State Representative - District 71  Bill Dean (R)                                  
GSL072DCLY State Representative - District 72  Kathleen Clyde (D)                             
GSL072RPAV State Representative - District 72  Gail Pavliga (R)                               
GSL073RLAR State Representative - District 73  Jeff LaRe (R)                                  
GSL074DSAK State Representative - District 74  Daniel Saks (D)                                
GSL074RWIL State Representative - District 74  Bernard Willis (R)                             
GSL075DMAT State Representative - District 75  Jan K. Materni (D)                             
GSL075RGHA State Representative - District 75  Haraz N. Ghanbari (R)                          
GSL076RJOH State Representative - District 76  Marilyn S. John (R)                            
GSL077DGOO State Representative - District 77  Mark D. Gooch (D)                              
GSL077RWIG State Representative - District 77  Scott Wiggam (R)                               
GSL078RMAN State Representative - District 78  Susan Manchester (R)                           
GSL079DEAS State Representative - District 79  Taylor Eastham (D)                             
GSL079RBLA State Representative - District 79  Monica Robb Blasdel (R)                        
GSL080RPOW State Representative - District 80  Jena Powell (R)                                
GSL081RHOO State Representative - District 81  James M. Hoops (R)                             
GSL082DMAR State Representative - District 82  Magdalene Markward (D)                         
GSL082RKLO State Representative - District 82  Roy W. Klopfenstein (R)                        
GSL083DOSB State Representative - District 83  Claire Osborne (D)                             
GSL083RCRO State Representative - District 83  Jon Cross (R)                                  
GSL084DROD State Representative - District 84  Sophia Rodriguez (D)                           
GSL084RKIN State Representative - District 84  Angela N. King (R)                             
GSL085RBAR State Representative - District 85  Tim Barhorst (R)                               
GSL086DLUK State Representative - District 86  Barbara A. Luke (D)                            
GSL086RRIC State Representative - District 86  Tracy Richardson (R)                           
GSL087RMCC State Representative - District 87  Riordan T. McClain (R)                         
GSL088DSEL State Representative - District 88  Dianne Selvey (D)                              
GSL088RCLI State Representative - District 88  Gary Click (R)                                 
GSL089DOBE State Representative - District 89  Jim Obergefell (D)                             
GSL089RSWE State Representative - District 89  D.J. Swearingen (R)                            
GSL090DDOD State Representative - District 90  Andrew Dodson (D)                              
GSL090RBAL State Representative - District 90  Brian Baldridge (R)                            
GSL091RPET State Representative - District 91  Bob Peterson (R)                               
GSL092RJOH State Representative - District 92  Mark Johnson (R)                               
GSL093RSTE State Representative - District 93  Jason Stephens (R)                             
GSL094DCON State Representative - District 94  Tanya Conrath (D)                              
GSL094REDW State Representative - District 94  Jay Edwards (R)                                
GSL095DRYA State Representative - District 95  William D. Ryan (D)                            
GSL095RJON State Representative - District 95  Don Jones (R)                                  
GSL096DDIP State Representative - District 96  Charlie DiPalma (D)                            
GSL096RFER State Representative - District 96  Ron Ferguson (R)                               
GSL097RHOL State Representative - District 97  Adam Holmes (R)                                
GSL098RKIC State Representative - District 98  Darrell D. Kick (R)                            
GSL099DZAP State Representative - District 99  Kathy Zappitello (D)                           
GSL099RART State Representative - District 99  Sarah Fowler Arthur (R)                        

**oh_2022_gen_prec_sldu.shp**
GSU01RMCC  State Senator - District 01  Robert McColley (R)                                   
GSU03DMAH  State Senator - District 03  Tina Maharath (D)                                     
GSU03RREY  State Senator - District 03  Michele Reynolds (R)                                  
GSU05RHUF  State Senator - District 05  Stephen A. Huffman (R)                                
GSU07DDAL  State Senator - District 07  David Dallas (D)                                      
GSU07RWIL  State Senator - District 07  Steve Wilson (R)                                      
GSU09DING  State Senator - District 09  Catherine D. Ingram (D)                               
GSU09RSON  State Senator - District 09  Orlando B. Sonza Jr (R)                               
GSU11DHIC  State Senator - District 11  Paula Hicks-Hudson (D)                                
GSU11RDIA  State Senator - District 11  Tony Dia (R)                                          
GSU13DELI  State Senator - District 13  Anthony Eliopoulos (D)                                
GSU13RMAN  State Senator - District 13  Nathan H. Manning (R)                                 
GSU15DCRA  State Senator - District 15  Hearcel F. Craig (D)                                  
GSU17DBOO  State Senator - District 17  Garry Boone (D)                                       
GSU17RWIL  State Senator - District 17  Shane Wilkin (R)                                      
GSU19DSWI  State Senator - District 19  Heather M. Swiger (D)                                 
GSU19RBRE  State Senator - District 19  Andrew O. Brenner (R)                                 
GSU21DSMI  State Senator - District 21  Kent Smith (D)                                        
GSU21RALT  State Senator - District 21  Mikhail Alterman (R)                                  
GSU23DANT  State Senator - District 23  Nickie J. Antonio (D)                                 
GSU23RSIM  State Senator - District 23  Landry M. Simmons Jr (R)                              
GSU25DDEM  State Senator - District 25  Bill DeMora (D)                                       
GSU25RWYS  State Senator - District 25  Chandler Wysocki (R)                                  
GSU27DGOE  State Senator - District 27  Patricia Goetz (D)                                    
GSU27RROE  State Senator - District 27  Kristina D. Roegner (R)                               
GSU29RSCH  State Senator - District 29  Kirk Schuring (R)                                     
GSU31RLAN  State Senator - District 31  Al Landis (R)                                         
GSU33DHAG  State Senator - District 33  Bob Hagan (D)                                         
GSU33RRUL  State Senator - District 33  Michael Anthony Rulli (R)                                                                 
                          
**oh_2022_gen_prec_no_splits.shp - contains all of the above fields/precinct geometries not split by district**                                                           

## Processing Steps
Visit the RDH GitHub and the processing script for this code [here](https://github.com/nonpartisan-redistricting-datahub/pber_collection)

## Additional Notes
UNIQUE_IDs that contain "ZZZ" are spatial areas within a county not contained within other precinct boundaries with zero voters.

Precinct boundaries were split according to SLDL, SLDU and congressional district boundaries to more accurately represent where votes occurred, particularly relevant for any disaggregation. This is why there is a separate shapefile for each district type. For All contests in one shapefile, see "oh_2022_gen_prec_no_splits.shp".

Files were checked against the original 2022 Election Results CSV file. Results matched exactly in all counties across all files except oh_2022_gen_prec_sldl.shp. 
When precinct geometries were split according to SLDL districts, the votes for district 55 were lost because UNIQUE_ID = WARREN-AHB is fully contained within district 56 spatially. This led to a loss of 15 and 58 votes across Warren County for GSL055DZOR and GSL055RLIP respectively.  


Ohio is made up of 88 counties and 26 of those counties changed precinct boundaries between the 2020 general election and 2022. 

26 counties that were not carried over:
{"brown","butler","clark","clermont","columbiana","cuyahoga","delaware", "erie","geauga","hamilton","hardin", 
 "hocking","lake","lucas","lorain","marion","medina","mercer","miami","montgomery","muskingum","pickaway","portage",
 "stark","tuscarawas","wood"}

Counties that provided 1:1 match with election results:
[clark, columbiana, delaware, geauga, hamilton, hardin, hocking, lake, marion, mercer, muskingum, tuscarawas]

Counties that provided 1:1 match with election results after dissolving cases with multiple geometries for a given precinct identifier:
[brown, butler, clermont, cuyahoga, erie, miami, montgomery, medina, lorain, lucas, pickaway, portage, stark, wood] 

Erie: Precinct "Bellevue City-Annexed-Refer to Board of Elections" only had two registered voters so the state BOE added those votes to "Groton" precinct. As a result the RDH combined the shapes for the two precincts to more accurately reflect the votes cast. 

Pickaway: SOS Codes "000" and "AG" in the Circleville shapefile overlapped with shapes from the County level file provided by Pickaway county and therefore were removed from the shapefile. 

Portage: The shapes from Tallmadge Township were combined with Brimfield A and E surrounding the two pieces as per email exchange with the county BOE. Two shapes cut from Ravenna Twp G are non-contiguous and had null precinct names in the shapefile. These were assigned to Ravenna Twp G. 
There is one precinct, in both 2017 and 2022 map, that is not named. Per Joe Reichlin it matches up with what the SoS calls "PRECINCT SUGAR BUSH KNOLLS". Additionally, there are several "extra" precincts that account for a military arsenal where there are no voters. As with other no voter precincts, these have been labeled "ZZZ". 

Wood: Wood County does not provide a county-wide precinct shapefile, instead they have individual shapefiles for every precinct. In the case of precinct NORTHWOOD A, also known as 810, the shapefile provided by the county has no geometry. As a result, the geometry for that precinct was pulled from the 2020 precinct shapefile.

Please direct questions related to processing this dataset to info@redistrictingdatahub.org.