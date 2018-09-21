# Files Description

This readme states the reasoning for each function and the order of which each function should be run. Most of the functions are run in the scripts folder; therefore, there is no real need to come to this folder unless you are a developer.

## Deployment

<dl>
  <dt>1. Convert GC's Matlab Structs to Python Dicts</dt>
  <dd>Script: uprite/python_data_structure.py</dd>
  <dd>Output: python pickle files (python_struct.pkl)<dd>
</dl>

<dl>
  <dt>2. Flag the data that is empty from UR</dt>
  <dd>Script: uprite/flag_empty_data.py</dd>
  <dd>Output: Overwritten python pickle file (python_struct.pkl) and csv file (uprite_data_overview.csv)</dd>
</dl>

<dl>
  <dt>3. Extract TO & HS from zeno walkway</dt>
  <dd>Script: uprite/extract_zeno.py</dd>
  <dd>Output: new python pickle file (zeno_hs_to.pkl) and csv file (zeno_hs_to.csv) </dd>
</dl>

<dl>
  <dt>4. Extract data window from uprite</dt>
  <dd>Script: uprite/data_window.py</dd>
  <dd>Output: new python pickle file (data_window.pkl) </dd>
</dl>

<dl>
  <dt>5. Extract Gravity Window from UR</dt>
  <dd>Script: uprite/gravity_window.py</dd>
  <dd>Output: new python pickle file (gravity_window.pkl) </dd>
</dl>

<dl>
  <dt>6. Extract to and hs from uprite sensor</dt>
  <dd>Script: uprite/extract_uprite.py</dd>
  <dd>Output: new python pickle file (uprite_hs_to.pkl) & plots</dd>
</dl>

<dl>
  <dt>7. Calculate gait parameters from zeno walkway</dt>
  <dd>Script: uprite/zeno_gait.py</dd>
  <dd>Output: new python pickle file (zeno_gait.pkl) & csv file </dd>
</dl>

<dl>
  <dt>8. Calculate gait parameters from uprite sensor</dt>
  <dd>Script: uprite/uprite_gait.py</dd>
  <dd>Output: new python pickle file (uprite_gait.pkl) & csv file </dd>
</dl>

<dl>
  <dt>9. Compare gait parameters from uprite and zeno sensors</dt>
  <dd>Script: uprite/compare_gait.py</dd>
  <dd>Output: new csv file (compare_gait.csv) </dd>
</dl>

<dl>
  <dt>10. Output HS and TO data from uprite and zeno sensors</dt>
  <dd>Script: uprite/print_hs_to.py</dd>
  <dd>Output: new csv file (hs_to_data.csv) </dd>
</dl>

### Miscellanous Files
<dl>
  <dt>11. Look at how the time-stamp of the uprite and zeno sensor compare </dt>
  <dd>Script: uprite/datestamp_window.py</dd>
  <dd>Output: None (just plots) </dd>
</dl>
