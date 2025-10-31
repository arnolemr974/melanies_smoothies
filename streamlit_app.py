# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
# Write directly to the app

st.title(f"Custom your smoothies :cup_with_straw:")
st.write(
  """Choose your fruits
  """
)
name_on_order = st.text_input('Name of Smoothie:')
st.write('The name of your Smoothie will be:', name_on_order)

#session = get_active_session()
cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

pd_df=my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
      'Choose up to 5 ingredients:' 
    , my_dataframe
    ,max_selections=5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        st.subheader(fruit_chosen + ' Nutrition Information')
        #smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    st.write(ingredients_string) 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('"""+ ingredients_string + """','"""+name_on_order+"""')"""
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        st.success('Your Smoothie is ordered!', icon="✅")
#st.text(smoothiefroot_response.json())
my_dataframe2 = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()
if my_dataframe2:
	editable_df = st.data_editor(my_dataframe)
	submitted = st.button('Submit')	
	if submitted:	

		og_dataset = session.table("smoothies.public.orders")
		edited_dataset = session.create_dataframe(editable_df)
		
		try:
			og_dataset.merge(edited_dataset
						 , (og_dataset['ORDER_UID'] == edited_dataset['ORDER_UID'])
						 , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
							)
			#st.success('Order updated', icon = '👍')	
		except:
			st.write('Something went wrong')
else:
    st.success('there are no pending orders right now', icon = '👍')	
