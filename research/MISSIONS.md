# Missions, measurements and public archives

This is an acquisition guide for a dichotomy study, covering the principal Mars science-return missions and historically limited returns. It does **not** claim a product-level audit of every mission, instrument or flyby. Mission dates below are arrival/encounter years, not claims of current operational status. Failed missions without useful Mars science returns are kept outside the evidence count. No future mission is treated as an existing observation.

Archive availability, public access and open-source software are different properties. Use product labels, calibration documentation, release dates and citation requirements from the archive before analysis. The links identify official access routes; some portals or products may require registration, and access to every individual product has not been tested.

## Orbital and historical context

| Mission / encounter | Relevant measurements | Use in this project | Archive or primary reference |
|---|---|---|---|
| Mariner 4 (1965), 6 and 7 (1969) | Images and atmospheric occultation | Historical baseline; limited spatial coverage | [NASA mission history](https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/more_on_mars/), [NSSDC catalog](https://nssdc.gsfc.nasa.gov/planetary/projectdata.html) |
| Mariner 9 (1971) | Orbital imaging and atmospheric observations | Early global geological context | [NASA history](https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/more_on_mars/) |
| Mars 2/3 (1971), 4/5/6/7 (1974) | Uneven orbital, flyby and descent returns | Historical coverage; no successful long-duration surface record from these landers | [NSSDC catalog](https://nssdc.gsfc.nasa.gov/planetary/projectdata.html) |
| Viking 1 and 2 orbiters (1976) | Imaging and atmospheric sounding | Surface chronology and historical change | [Mars ODE](https://ode.rsl.wustl.edu/mars/) |
| Phobos 2 (1989) | Limited Mars/Phobos observations | Historical thermal/plasma context; limited duration | [NSSDC catalog](https://nssdc.gsfc.nasa.gov/planetary/projectdata.html) |
| Mars Global Surveyor (1997) | MOLA topography, MAG/ER magnetism, TES spectra, imaging and tracking | Base layers for relief, crustal magnetism, composition and gravity | [PDS MGS holdings](https://pds-geosciences.wustl.edu/missions/mgs/) |
| Mars Odyssey (2001) | THEMIS thermal imaging; gamma-ray and neutron measurements; tracking | Surface thermophysics, elemental/hydrogen distributions and gravity | [NASA Odyssey](https://science.nasa.gov/mission/odyssey/), [PDS services](https://pds-geosciences.wustl.edu/dataserv/default.htm) |
| Mars Express (2003) | HRSC, OMEGA, MARSIS, MaRS and atmosphere instruments | Relief, mineralogy, buried interfaces and occultation constraints | [ESA instruments](https://www.esa.int/Science_Exploration/Space_Science/Mars_Express/Mars_Express_orbiter_instruments), [PSA](https://psa.esa.int/) |
| Mars Reconnaissance Orbiter (2006) | HiRISE/CTX imaging, CRISM spectra, SHARAD radar, MCS atmosphere, tracking | Boundary geology, composition, stratigraphy, thermal context and gravity | [NASA MRO](https://science.nasa.gov/mission/mars-reconnaissance-orbiter/), [ODE](https://ode.rsl.wustl.edu/mars/) |
| Mars Orbiter Mission (2014) | MCC, TIS, MSM, LAP and MENCA | Regional/global imaging and atmospheric context | [ISRO public release](https://www.isro.gov.in/mission_mars_orbiter_mom_released.html), [MOM archive](https://mrbrowse.issdc.gov.in/MOMLTA/) |
| MAVEN (2014) | Magnetic field, particles and upper-atmosphere measurements | Crustal-field refinement and atmospheric escape; separate external fields | [NASA MAVEN](https://science.nasa.gov/mission/maven/), [PDS](https://pds.nasa.gov/) |
| ExoMars Trace Gas Orbiter (2016) | ACS/NOMAD, CaSSIS and FREND | Atmospheric composition, surface context and shallow hydrogen | [ESA instruments](https://www.esa.int/Science_Exploration/Human_and_Robotic_Exploration/Exploration/ExoMars/Trace_Gas_Orbiter_instruments), [PSA](https://psa.esa.int/) |
| Hope / Emirates Mars Mission (2021) | Atmospheric imaging and infrared/UV observations | Seasonal and local-time atmospheric variability | [EMM Science Data Center](https://sdc.emiratesmarsmission.ae/) |
| Tianwen-1 orbiter (2021) | Imaging, mineralogical, radar, magnetic and particle observations | Additional global/regional constraints; audit data access per paper | [CNSA mission report](https://www.cnsa.gov.cn/english/n6465652/n6465653/c6840321/content.html), [Zhurong magnetic study and data statement](https://doi.org/10.1038/s41550-023-02008-7) |

A radar reflector is not uniquely an ice or liquid-water interface. Dielectric properties, clutter and geometry must be tested before assigning composition. Likewise, orbital spectroscopy primarily samples exposed surface material, whereas gravity and magnetism integrate much greater depths. These are methodological comparison requirements, not interchangeable maps of the same material.

## Surface context

| Mission / arrival | Measurements most useful here | Dichotomy relevance and limits | Access route |
|---|---|---|---|
| Viking 1 and 2 landers (1976) | Local images, chemistry and meteorology | Historical local context; no global crustal sampling | [NASA historical overview](https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/more_on_mars/), [PDS](https://pds.nasa.gov/) |
| Pathfinder / Sojourner (1997) | Imaging, rock chemistry and meteorology | Ares Vallis transported materials and surface processes | [NASA history](https://www.jpl.nasa.gov/news/press_kits/mars_2020/launch/more_on_mars/), [PDS](https://pds.nasa.gov/) |
| Spirit and Opportunity (2004) | Rock chemistry/mineralogy, imaging and geological context | Gusev and Meridiani alteration histories; local and younger than much primordial crust | [PDS landed-mission services](https://pds-geosciences.wustl.edu/dataserv/default.htm) |
| Phoenix (2008) | Soil/ice chemistry, imaging and meteorology | Northern high-latitude volatile environment; shallow local sampling | [PDS services](https://pds-geosciences.wustl.edu/dataserv/default.htm) |
| Curiosity / MSL (2012) | CheMin, SAM, ChemCam/APXS, imaging and weather | Gale stratigraphy, mineralogy, chemistry and isotopes; not representative of a whole hemisphere | [NASA instruments](https://science.nasa.gov/mission/msl-curiosity/science-instruments/), [PDS services](https://pds-geosciences.wustl.edu/dataserv/default.htm) |
| InSight (2018) | SEIS, RISE, pressure/wind and magnetometer observations | Crust/core anchor, seismic noise and a local magnetic constraint | [PDS InSight](https://pds-geosciences.wustl.edu/missions/insight/) |
| Perseverance (2021) | Imaging, SuperCam, PIXL, SHERLOC, RIMFAX, MEDA and contextualized cores | Jezero geology and prospective laboratory samples; no rover paleointensity determination | [NASA instruments](https://science.nasa.gov/mission/mars-2020-perseverance/science-instruments/), [Mansbach et al., 2024](https://doi.org/10.1029/2024JE008505) |
| Zhurong (2021) | Ground magnetic, radar, imaging, compositional and weather observations | A rare Utopia ground transect; spatially restricted | [Du et al., 2023](https://doi.org/10.1038/s41550-023-02008-7), [CNSA](https://www.cnsa.gov.cn/english/n6465652/n6465653/c6840321/content.html) |
| Ingenuity (2021) | Aerial imaging and flight/atmospheric context | Local reconnaissance and technical context; not a global geophysical survey | [NASA Mars 2020](https://science.nasa.gov/mission/mars-2020-perseverance/) |

InSight's HP3 experiment must not be listed as a completed deep heat-flow measurement: the intended subsurface deployment did not succeed. Use the released experiment products for what they actually measured. [NASA instrument documentation](https://science.nasa.gov/mission/insight/science-instruments/).

Schiaparelli returned descent engineering/science context before impact, and MarCO demonstrated relay during a flyby; neither supplies a successful long-lived surface geophysical station. Other failed attempts and planned missions do not provide the dichotomy measurements sought here. Earth's telescopes, laboratory experiments and spacecraft gravity tracking remain complementary evidence sources outside this surface/orbiter classification.

## First data acquisition manifest

| Priority | Data product | Why acquire it | Required controls |
|---|---|---|---|
| 1 | MOLA topography plus a documented global crustal-thickness model | Define relief and structural provinces | Areoid/reference radius, coordinates, density assumption, model version |
| 1 | MGS/MAVEN crustal-field model | Compare magnetism with geological units at matched resolution | Harmonic normalization, evaluation altitude, truncation and external-field treatment |
| 1 | [USGS global geological map](https://www.usgs.gov/maps/geologic-map-mars) | Separate geological provinces, ages and resurfacing | Unit definitions, map scale and chronological uncertainty |
| 2 | Odyssey GRS and OMEGA/CRISM products | Test carrier/composition and heat-production hypotheses | Footprints, dust/exposure, detection thresholds and depth mismatch |
| 2 | InSight SEIS and environmental channels | Test location/path and noise effects | Instrument response, event catalog, time standards and atmosphere removal |
| 2 | MARSIS/SHARAD profiles | Test burial and interfaces across selected transects | Clutter simulation, dielectric assumptions and track coverage |
| 3 | Meteorite analytical tables and provenance hypotheses | Relate dated rock histories to inferred provinces | Pairings, launch groups, alteration, specimen history and age semantics |
| 3 | Seasonal MCD surface pressure | Evaluate atmospheric-loading corrections in gravity analysis | Surface altitude mode, common universal time, area weighting and scenario ensemble |

Use [SPICE mission geometry](https://naif.jpl.nasa.gov/naif/data_mars.html) where required. The [ODE](https://ode.rsl.wustl.edu/) and [PDS Geosciences tools](https://pds-geosciences.wustl.edu/dataserv/default.htm) provide cross-mission discovery, but every derived product still needs its own citation and calibration audit.

**Acquisition status in this release:** MOLA, MGS/MAVEN coefficients, equivalent magnetic source depths, the InSight crustal archive, thermal outputs, USGS geologic units, meteorite tables and NWA 7034 laboratory measurements have been downloaded. See the [source manifest](data/manifest.json) and [executed diagnostics](FIRST_RESULTS.md). Additional radar, calibrated surface magnetometer and mineral/elemental products remain to be acquired and harmonized. The existing MCD installation serves the atmosphere app.
