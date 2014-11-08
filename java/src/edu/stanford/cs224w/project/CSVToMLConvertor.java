package edu.stanford.cs224w.project;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Scanner;
import java.util.Set;

import org.apache.commons.collections15.ClosureUtils;
import org.apache.commons.collections15.CollectionUtils;
import org.apache.commons.collections15.Predicate;
import org.apache.commons.collections15.functors.PredicateTransformer;

import com.ctc.wstx.util.StringUtil;

import edu.uci.ics.jung.algorithms.cluster.BicomponentClusterer;
import edu.uci.ics.jung.algorithms.cluster.EdgeBetweennessClusterer;
import edu.uci.ics.jung.algorithms.cluster.VoltageClusterer;
import edu.uci.ics.jung.graph.DirectedSparseGraph;
import edu.uci.ics.jung.graph.Graph;
import edu.uci.ics.jung.graph.UndirectedSparseGraph;
import edu.uci.ics.jung.graph.util.EdgeType;
import edu.uci.ics.jung.io.GraphMLWriter;

public class CSVToMLConvertor
{

	public static void main(String[] args) throws IOException
	{
		File input = new File("payment_graph_physician_company.csv");
//		File output = new File("payment_graph_physician_company_ml.xml");
		File output = new File("payment_graph_physician_physician_ml.xml");
		Graph<Long, Object> g = new UndirectedSparseGraph<Long, Object>();
		BufferedReader reader = new BufferedReader(new FileReader(input));
		Map<Long, List<Long>> dictionary= new HashMap<Long, List<Long>>();
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
				if(dictionary.containsKey(v2))
				{
					List<Long> providers = dictionary.get(v2);
					providers.add(v1);
				}
				else
				{
					List<Long> providers = new ArrayList<>();
					providers.add(v1);
					dictionary.put(v2, providers);
				}
			}
			
//			WeightedEdge edge = new WeightedEdge("Edge: " + v1 + "-" + v2, w1);
//			if(!g.containsVertex(v1))
//			{
//				g.addVertex(v1);
//				if(dictionary.containsKey(v2))
//				{
//					Set<Long> providers = dictionary.get(v2);
//					for(Long provider: providers)
//					{
//						g.addEdge("Edge: " + v1 + "-" + provider, v1, provider, EdgeType.UNDIRECTED);
//					}
//					providers.add(v1);
//				}
//				else
//				{
//					Set<Long> providers = new HashSet<Long>();
//					providers.add(v1);
//					dictionary.put(v2, providers);
//				}
//			}
//			if(!g.containsVertex(v2))
//			{
//				g.addVertex(v2);
//			}
//			else
//			{
//				
//			}
//			if(!g.containsEdge(edge))
//			{
//				g.addEdge(edge, v1, v2, EdgeType.DIRECTED);
//			}
			
		}
		
//		for(Long key:dictionary.keySet())
//		{
//			List<Long> providers = dictionary.get(key);
//			for(Long provider:providers)
//			{
//				g.addVertex(provider);
//				for(Long otherProvider:providers)
//				{
//					if(provider!=otherProvider)g.addEdge("[Edge: " + provider + "-" + otherProvider + "]", provider, otherProvider, EdgeType.UNDIRECTED);
//				}
//			}
//			providers.clear();
//		}
		
//		edgeBetweennessCommunity(g, "edge_betweeness_community_1.txt");
//		bicomponentCommunity(g, "voltage_community.txt");
		
//		BufferedWriter writer = new BufferedWriter(new FileWriter(output));
//		GraphMLWriter<Long, Object> gWriter = new GraphMLWriter<Long, Object>();
//		
//		gWriter.save(g, writer);
//		
//		reader.close();
		
		BufferedWriter writer = new BufferedWriter(new FileWriter(new File("provider_provider_network_1000.txt")));
		for(Long key:dictionary.keySet())
		{
			List<Long> providers = dictionary.get(key);
			for(Long provider:providers)
			{
				for(Long otherProvider:providers)
				{
					if(provider!=otherProvider)
					{
						writer.write(provider + "\t" + otherProvider);
						writer.newLine();
					}
				}
			}
			providers.clear();
		}
		writer.flush();
		writer.close();

	}
	
	private static void bicomponentCommunity(Graph<Long, WeightedEdge> g, String fileName) throws IOException
	{
		VoltageClusterer<Long, WeightedEdge> cluster1 = new VoltageClusterer<Long, WeightedEdge>(g, 20);
		Collection<Set<Long> > cluster = cluster1.cluster(20);//cluster1.transform(g);
		BufferedWriter communityWriter1 = new BufferedWriter(new FileWriter(new File(fileName)));
		Iterator<Set<Long>> iterator = cluster.iterator();
		
		while(iterator.hasNext())
		{
			Set<Long> community = iterator.next();
			Iterator<Long> nodes = community.iterator();
			while(nodes.hasNext())
			{
				Long value = nodes.next();
				communityWriter1.write(value.toString());
				if(nodes.hasNext())
				{
					communityWriter1.write("\t");
				}
				
			}
			communityWriter1.newLine();
			communityWriter1.flush();
		}
		
		communityWriter1.close();
	}
	
	private static void edgeBetweennessCommunity(Graph<Long, Object> g, String fileName) throws IOException
	{
		EdgeBetweennessClusterer<Long, Object> cluster1 = new EdgeBetweennessClusterer<Long, Object>(1);
		Set<Set<Long> > cluster = cluster1.transform(g);
		BufferedWriter communityWriter1 = new BufferedWriter(new FileWriter(new File(fileName)));
		Iterator<Set<Long>> iterator = cluster.iterator();
		
		while(iterator.hasNext())
		{
			Set<Long> community = iterator.next();
			Iterator<Long> nodes = community.iterator();
			while(nodes.hasNext())
			{
				Long value = nodes.next();
				communityWriter1.write(value.toString());
				if(nodes.hasNext())
				{
					communityWriter1.write("\t");
				}
				
			}
			communityWriter1.newLine();
			communityWriter1.flush();
		}
		
		communityWriter1.close();
	}
	

}
