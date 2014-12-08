package edu.stanford.cs224w.project;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.apache.commons.collections15.CollectionUtils;
import org.apache.commons.collections15.Predicate;

public class GroundTruth_V2
{

	public static void main(String[] args) throws IOException
	{
		File input = new File("payment_graph_physician_company.csv");
		BufferedReader reader = new BufferedReader(new FileReader(input));
		Map<Long, HashMap<Long, Boolean>> dictionary= new HashMap<Long, HashMap<Long, Boolean>>();
		HashMap<Long, Boolean> allProviders = new HashMap<Long, Boolean>();
		int line = 0;
		String s = null;
		int paymentThreshold = 1000;
		while((s = reader.readLine())!=null )
		{
			String[] inputs = s.split("\t");
			String npi = inputs[0];
			String companyId = inputs[1];
			String amount = "0";
			if(inputs.length > 2)
			{
				amount = inputs[2];
			}
			if(line++==0)
			{
				continue;
			}
			long v1 = 0l;
			long v2 = 0l;
			double w1 = 0d;
			try
			{
				v1 = Long.valueOf(npi.trim());
			}
			catch(Exception e){}
			try
			{
				v2 = Long.valueOf(companyId.trim());
			}
			catch(Exception e){}
			try
			{
				w1 = Double.valueOf(amount.trim());
			}
			catch(Exception e){}
			if(w1 > paymentThreshold)
			{
				if(!allProviders.containsKey(v1))
				{
					allProviders.put(v1, false);
				}
				if(dictionary.containsKey(v2))
				{
					Map<Long, Boolean> providers = dictionary.get(v2);
					providers.put(v1, true);
				}
				else
				{
					@SuppressWarnings("unchecked")
               HashMap<Long, Boolean> providers = (HashMap<Long, Boolean>) allProviders.clone();
					providers.put(v1, true);
					dictionary.put(v2, providers);
				}
				for(Long company:dictionary.keySet())
				{
					if(company.longValue()==v2) continue;
					Map<Long, Boolean> providers = dictionary.get(company);
					if(providers.containsKey(v1))continue;
					else
					{
						providers.put(v1, false);
					}
				}
			}
		}
		reader.close();
		
		HashMap<Long, HashMap<Long, Boolean>> agmVector= new HashMap<Long, HashMap<Long, Boolean>>();
		for(Long company:dictionary.keySet())
		{
			agmVector.put(company, allProviders);
		}
		
		input = new File("project/community_full.txt");
		reader = new BufferedReader(new FileReader(input));
		List<List<Long>> doctors = new ArrayList<List<Long>>();
//		BufferedWriter writer = new BufferedWriter(new FileWriter("project/ground_truth_full_v2.txt"));
		while((s = reader.readLine())!=null )
		{
			List<Long> docInCommunity = new ArrayList<Long>();
			String[] docs = s.split("\t");
			for(String doc:docs)
			{
				docInCommunity.add(Long.valueOf(doc.trim()));
			}
			doctors.add(docInCommunity);
		}
		reader.close();
		
		
		for(int i=0;i<doctors.size();i++)
		{
			final List<Long> docs = doctors.get(i);
			for(Long company : agmVector.keySet())
			{
				final HashMap<Long, Boolean> providers = agmVector.get(company);
				
				for(Long doc: docs) {
					providers.put(doc, true);
				}
				
			}
//			Collection<Long> common = CollectionUtils.intersection(docs, matchedNpis);
			
//			writer.write("Community: " + i + " found overlap in " + matchingCommunities + ", totalMatches(MDs): " + common.size() + 
//					", missed(MDs): " + (matchedNpis.size() - common.size()) + ", Companies Involved in this community: " + companyIds);
//			writer.newLine();
		}
		
//		writer.close();

	}

}
