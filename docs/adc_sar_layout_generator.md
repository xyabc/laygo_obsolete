# SAR ADC generator

This example generates a asynchronous SAR ADC.

#### File description

Layout generators

adc_sar_capdac_layout_generator.py
- differential capdac

adc_sar_salatch_pmos_layout_generator.py
- PMOS side StrongArm latch

adc_sar_salatch_pmos_vanilla_layout_generator.py
- PMOS side StrongArm latch generator without spacing region

adc_sar_capdrv_layout_generator.py
- Cap driver

adc_sar_capdrv_array_layout_generator.py
- Cap driver array

adc_sar_sarafe_layout_generator.py
- SAR ADC analog frontend (capdac+capdrv+salatch) generator

adc_sar_sarclkgen_layout_generator.py
- SAR ADC clock generator

adc_sar_sarclkdelay_layout_generator.py
- SAR ADC clock delay

adc_sar_sarfsm_layout_generator.py
- SAR ADC FSM

adc_sar_sarlogic_layout_generator.py
- SAR ADC sarlogic

adc_sar_sarlogic_array_layout_generator.py
- SAR ADC sarlogic array

adc_sar_sarret_layout_generator.py
- SAR ADC output retimer

adc_sar_sarabe_layout_generator.py
- SAR ADC analog backend (clock, fsm, sarlogic, retimer)

adc_sar_layout_generator.py
- SAR ADC top

#### Installation
1. Set up a bag workspace.

2. Set up laygo.
Make sure you have proper laygo_config.yaml in your workspace.
And you should have primitive template & grid libraries & files for your tech.
Check lab2_a_gridlayoutgenerator_constructtemplate.py for reference.

3. Copy or make symbolic links of generator files in the bag working directory.

4. Edit cds.lib to read adc_sar_templates library.

5. Run bag and bag_adc_sar_import.py. Design modules are generated
 in BagModule/adc_sar_templates.

6. Overwrite the generated BagModule files with example files in BagModules/adc_sar_templates

7. Run layout generator scripts in a sequence shown above

#### Testbench
#StrongARM verification
1. Make sure testbench library is included in cds.lib
DEFINE adc_sar_testbenches ./laygo/generators/adc_sar_testbenches